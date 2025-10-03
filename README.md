# TIXBUSTER

**Generic voucher code bruteforcer for Pretix ticketing systems**

Systematically tests voucher codes against Pretix-based ticket platforms with rate limiting, session validation, and intelligent pattern generation.

## Features

- 🎯 **2,151+ built-in patterns** from common voucher naming conventions
- 🔒 **Session validation** with control test
- ⚡ **Rate limiting protection** with adaptive delays and auto-throttling
- 🔥 **Multi-threading support** (1-10 threads for parallel testing)
- 🎲 **Random bruteforce** with configurable patterns, prefixes, and charsets
- 🔍 **Multiple search modes** (priority, full scan, custom wordlist, random)
- 📊 **Detailed statistics** and result categorization
- 🛡️ **Cloudflare detection** and handling
- 🎯 **Auto-exit on success** with epic banner

## Quick Start

```bash
# 1. Update cookies in src/session.py
# 2. Validate session
python3 main.py validate

# 3. Test priority codes (36 highest probability)
python3 main.py test --priority

# 4. Test all patterns with multi-threading (~10-20 minutes with 5 threads)
python3 main.py test --all --threads 5

# 5. Random bruteforce if you know the pattern
# Example: if voucher is WTFLOL, this should find it
python3 main.py test --random 50 --random-prefix WTFLO --random-length 1 --random-charset upper --verbose
```

## Installation

No dependencies beyond Python 3.6+ standard library + `requests`:

```bash
pip install requests
# or
uv pip install requests
```

## Configuration

Edit `src/session.py` to update your session cookies:

```python
DEFAULT_COOKIES = {
    '__Host-pretix_csrftoken': 'YOUR_CSRF_TOKEN',
    '__Host-pretix_session': 'YOUR_SESSION_TOKEN',
    'cf_clearance': 'YOUR_CF_CLEARANCE'
}
```

Get these from your browser DevTools → Network tab → any Pretix request → Cookie header.

## CLI Commands

### Validate Session
```bash
python3 main.py validate [--verbose]
```

Tests session validity using a control voucher code.

### Test Vouchers

```bash
# Priority codes only (~2-3 minutes single-threaded)
python3 main.py test --priority

# All patterns with multi-threading (~10-20 minutes with 5 threads)
python3 main.py test --all --threads 5

# Aggressive multi-threading with no auto-throttling (~5-10 minutes, 10 threads)
python3 main.py test --all --threads 10 --no-brakes

# Random bruteforce (100 random 6-char codes A-Z,0-9)
python3 main.py test --random 100

# Random with DARK prefix (like DARKAB12CD, DARK99ZZQQ)
python3 main.py test --random 50 --random-prefix DARK --random-length 6

# Random with FREE suffix (like KK3DFREE, X9Y1FREE)
python3 main.py test --random 50 --random-suffix FREE --random-length 4

# Targeted bruteforce if you know part of the code
# Example: if voucher is WTFLOL, this should find it
python3 main.py test --random 50 --random-prefix WTFLO --random-length 1 --random-charset upper --verbose

# Custom wordlist
python3 main.py test --wordlist my_codes.txt

# Verbose output
python3 main.py test --priority --verbose

# Custom output file
python3 main.py test --priority --output my_results.json
```

### Statistics

```bash
# Show wordlist stats
python3 main.py stats

# Include priority codes list
python3 main.py stats --show-priority
```

### Search Patterns

```bash
# Find codes containing specific text
python3 main.py search GUEST
python3 main.py search VIP
python3 main.py search 2025
```

### Export Wordlist

```bash
# Export all patterns
python3 main.py export full_wordlist.txt

# Export priority only
python3 main.py export priority.txt --priority
```

## Wordlist Categories

| Category | Count | Description |
|----------|-------|-------------|
| Speakers | 882 | Common speaker name patterns |
| Variations | 840 | Pronoun + adjective combinations |
| CTF Patterns | 85 | Encodings, flags, leetspeak |
| Events | 73 | Generic event naming patterns |
| Common | 68 | GUEST, FREE, VIP, DISCOUNT, etc. |
| Venue | 56 | Venue-related patterns |
| Sponsors | 49 | Sponsor naming patterns |
| Movements | 45 | Tech movement keywords |
| Names | 32 | Common name patterns |
| Themes | 28 | Generic theme keywords |

## Response Types

| Status | Meaning |
|--------|---------|
| **SUCCESS** | Valid, active voucher code |
| **EXPIRED** | Valid format but expired |
| **USED** | Already redeemed |
| **LIMITED** | Usage limit reached |
| **UNKNOWN** | Unexpected response (investigate) |
| **NOTFOUND** | Invalid code (404) |

## Project Structure

```
tixbuster/
├── main.py                # CLI interface
├── src/
│   ├── __init__.py
│   ├── wordlist.py       # 2151 patterns
│   ├── tester.py         # Core testing engine
│   └── session.py        # Session management
├── data/
│   └── custom.txt        # Custom patterns (optional)
└── README.md
```

## Pattern Generation

Patterns are generated from common voucher naming conventions:

- **Generic discounts**: GUEST, FREE, VIP, DISCOUNT10, SAVE20, etc.
- **Encodings**: Base64, hex, ROT13
- **Leetspeak**: H4CK3R, FR33, T1CK3T
- **Date patterns**: 2024, 2025, JAN2025, etc.
- **Role-based**: SPEAKER, ORGANIZER, STAFF, MEDIA, PRESS
- **Event-generic**: EARLYBIRD, LATEBIRD, EXCLUSIVE, etc.

## Rate Limiting

Built-in protections:
- Adaptive delays (0.5-2.0s base + jitter)
- Automatic backoff on 429 responses
- Cloudflare challenge detection
- Request count tracking

## Results Output

Results saved to `results.json` (or custom path):

```json
{
  "SUCCESS": [],        // Valid codes
  "EXPIRED": [],        // Expired codes
  "USED": [],          // Already used
  "LIMITED": [],       // Hit usage limit
  "UNKNOWN": [],       // Unexpected responses
  "NOTFOUND": [],      // Invalid codes
  "tested": 0          // Total tested
}
```

## Custom Wordlists

Create `data/custom.txt`:

```
# Custom voucher codes
# One per line, comments with #

MYCODE2025
CUSTOMPATTERN
SPECIALGUEST
```

Then test:
```bash
python3 main.py test --wordlist data/custom.txt
```

## Performance

- **Priority codes**: ~2-3 minutes (36 codes, single-threaded)
- **Full scan single-threaded**: ~60-90 minutes (2,151 codes)
- **Full scan multi-threaded (5 threads)**: ~10-20 minutes (2,151 codes)
- **Full scan aggressive (10 threads, --no-brakes)**: ~5-10 minutes (2,151 codes)
- **Rate**: ~0.5-1.0 req/s (single), ~4-5 req/s (5 threads), ~8-10 req/s (10 threads)
- **Memory**: < 50MB (single), < 100MB (10 threads)
- **Auto-throttling**: Slows down on consecutive 429/403 errors (disable with `--no-brakes`)

## Strategy Tips

1. Start with priority codes (highest probability)
2. Use multi-threading for faster scans (`--threads 5` is safe, `--threads 10` is aggressive)
3. If you know part of the voucher pattern, use random bruteforce with prefix/suffix
4. Monitor for EXPIRED codes (indicates valid format)
5. Use `--verbose` to understand response patterns
6. Check UNKNOWN responses manually
7. Add successful patterns to custom wordlist
8. Tool auto-exits on first SUCCESS - you'll know immediately when a valid code is found

## Ethical Notice

Look, we get it - some folks are broke af and just want to network at conferences. While this tool *could* theoretically help with that in rare edge cases, **it's absolutely not recommended nor is this software intended for such actions**.

This tool is for:
- ✅ Security research on systems you own/have permission to test
- ✅ CTF challenges and competitions
- ✅ Authorized penetration testing

**Not for:**
- ❌ Unauthorized access attempts
- ❌ Fraud or theft
- ❌ Violating terms of service

Don't be a dick. Support conferences if you can afford it.

## Credits & Attribution

Built for testing [pretix](https://github.com/pretix/pretix) ticketing systems.

- **Pretix**: Open-source ticketing and event management platform
- **Documentation**: https://docs.pretix.eu/
- **GitHub**: https://github.com/pretix/pretix
- **License**: Apache 2.0

## Roadmap

### Completed Features ✅

- [x] **Multi-threading Support** (v0.0.1)
  - ThreadPoolExecutor for parallel requests
  - Configurable thread count (`--threads 1-10`)
  - Per-thread session management
  - Auto-throttling on consecutive rate limits
  - `--no-brakes` flag to disable throttling

- [x] **Random Bruteforce Pattern Generation** (v0.0.1)
  - Generate random codes with configurable patterns
  - Multiple charset options (upper, lower, alphanum, uppernumeric)
  - Prefix/suffix support for targeted bruteforce
  - Configurable code length

- [x] **Auto-exit on Success** (v0.0.1)
  - Stops immediately when valid voucher found
  - Epic success banner
  - Thread pool cancellation on success

### Planned Features

- [ ] **Automated Wordlist Generation from Web Content**
  - Fetch event landing page
  - Crawl program/schedule for talk titles
  - Extract speaker names automatically
  - Generate targeted wordlist from scraped content
  - Output to `data/generated_wordlist.txt`

- [ ] **Generic Target URL Support**
  - Remove hardcoded darkprague.com
  - Add `--url` / `-u` CLI argument
  - Support any Pretix instance

- [ ] **WAF Detection & Adaptive Throttling Improvements**
  - Detect Cloudflare, Imperva, and other WAFs
  - Interactive prompt when throttled (sqlmap-style: "Continue? [Y/n]")
  - More sophisticated auto-adjustment algorithms

- [ ] **Pretix Permission Enumeration**
  - Check https://docs.pretix.eu/dev/development/implementation/permissions.html
  - Detect permission misconfigurations
  - Enumerate available API endpoints
  - Test for authorization bypasses

### Community

PRs welcome for any features!

## License

MIT License - Educational and research purposes only.

## Contributing

PRs welcome for:
- New generic pattern categories
- Performance improvements
- Additional Pretix API endpoints
- Better rate limiting strategies

---

**TIXBUSTER** - Because sometimes the tickets just want to be free 🎫
