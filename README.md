# TIXBUSTER

**Generic voucher code bruteforcer for Pretix ticketing systems**

Systematically tests voucher codes against Pretix-based ticket platforms with rate limiting, session validation, and intelligent pattern generation.

## Features

- **Built-in pattern wordlists** from common voucher naming conventions
- **Session validation** with control test
- **Rate limiting protection** with adaptive delays and auto-throttling
- **Multi-threading support** (1-10 threads for parallel testing)
- **Random bruteforce** with configurable patterns, prefixes, and charsets
- **Multiple search modes** (priority, full scan, custom wordlist, random)
- **Wordlist generation** from event websites (speakers, talks, sponsors)
- **Detailed statistics** and result categorization
- **Cloudflare detection** and handling
- **Auto-exit on success** with epic banner

## Quick Start

```bash
# 1. Install dependencies
uv pip install requests python-dotenv

# 2. Copy .env.example to .env and configure your cookies
cp .env.example .env
# Edit .env with your browser cookies (see Configuration below)

# 3. Validate session (replace with your target Pretix instance)
python3 main.py validate tix.darkprague.com

# 4. Test priority codes
python3 main.py test tix.darkprague.com --priority

# 5. Test all patterns with multi-threading (~10-20 minutes with 5 threads)
python3 main.py test tix.darkprague.com --all --threads 5

# 6. Random bruteforce if you know the pattern
# Example: if voucher is WTFLOL, this should find it
python3 main.py test tix.darkprague.com --random 50 --random-prefix WTFLO --random-length 1 --random-charset upper --verbose
```

## Installation

Using `uv` (recommended):

```bash
uv pip install requests python-dotenv
```

Or using `pip`:

```bash
pip install requests python-dotenv
```

## Configuration

**Prerequisites:** You need a valid browser session with the Pretix instance.

### Cookie Extraction

TIXBUSTER requires 3 cookies and 1 CSRF token from your browser session:

1. **Open your browser DevTools** (F12 or Right-click → Inspect)
2. **Go to Network tab**
3. **Add an item to cart** on the Pretix site (any item, any quantity)
4. **Find the `/cart/voucher` request** in the Network tab
5. **Click on it and go to Headers section**
6. **Copy the following from the Cookie header:**
   - `__Host-pretix_csrftoken` - CSRF cookie
   - `__Host-pretix_session` - Session cookie
   - `cf_clearance` - Cloudflare clearance (if present)
7. **Copy the CSRF middleware token** from the request payload (Form Data section):
   - `csrfmiddlewaretoken` - CSRF token

### Setting Up .env

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and paste your extracted values:

```bash
# Required: CSRF cookie from Cookie header
PRETIX_CSRF_COOKIE=your_csrf_cookie_here

# Required: Session cookie from Cookie header
PRETIX_SESSION=your_session_cookie_here

# Required: CSRF middleware token from request payload
PRETIX_CSRF_TOKEN=your_csrf_middleware_token_here

# Optional: Cloudflare clearance (only if Cloudflare protection active)
PRETIX_CF_CLEARANCE=your_cloudflare_clearance_here
```

**Note:** The `.env` file is git-ignored and will not be committed.

**Target URL:** The Pretix instance URL is specified as a command-line argument, not in `.env`:

```bash
# Short form (https:// is added automatically)
python3 main.py test tix.darkprague.com --priority

# Full URL form
python3 main.py test https://tix.darkprague.com --priority
```

## CLI Commands

### Validate Session
```bash
python3 main.py validate <url> [--verbose]

# Examples
python3 main.py validate tix.darkprague.com
python3 main.py validate https://tix.example.com --verbose
```

Tests session validity using a control voucher code.

### Test Vouchers

```bash
# Priority codes only (~2-3 minutes single-threaded)
python3 main.py test tix.darkprague.com --priority

# All patterns with multi-threading (~10-20 minutes with 5 threads)
python3 main.py test tix.darkprague.com --all --threads 5

# Aggressive multi-threading with no auto-throttling (~5-10 minutes, 10 threads)
python3 main.py test tix.darkprague.com --all --threads 10 --no-brakes

# Random bruteforce (100 random 6-char codes A-Z,0-9)
python3 main.py test tix.darkprague.com --random 100

# Random with DARK prefix (like DARKAB12CD, DARK99ZZQQ)
python3 main.py test tix.darkprague.com --random 50 --random-prefix DARK --random-length 6

# Random with FREE suffix (like KK3DFREE, X9Y1FREE)
python3 main.py test tix.darkprague.com --random 50 --random-suffix FREE --random-length 4

# Targeted bruteforce if you know part of the code
# Example: if voucher is WTFLOL, this should find it
python3 main.py test tix.darkprague.com --random 50 --random-prefix WTFLO --random-length 1 --random-charset upper --verbose

# Custom wordlist
python3 main.py test tix.darkprague.com --wordlist my_codes.txt

# Verbose output
python3 main.py test tix.darkprague.com --priority --verbose

# Custom output file
python3 main.py test tix.darkprague.com --priority --output my_results.json

# Works with any Pretix instance
python3 main.py test tix.otherconf.com --priority
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

## Custom Wordlists

TIXBUSTER supports loading custom wordlists from files. You can:

1. **Use built-in wordlists** - Generated from common patterns
2. **Generate from event websites** - Use `generate-wordlist` command to scrape speakers/talks/sponsors
3. **Use external wordlists** - Like [SecLists](https://github.com/danielmiessler/SecLists)

### Wordlist Format

One voucher code per line, uppercase recommended, comments with `#`:

```
# My custom voucher codes
SPECIALCODE2025
GUESTPASS
VIP2025
# Add more codes below
```

### Using SecLists

SecLists contains useful password/pattern dictionaries that can be adapted for vouchers:

```bash
# Clone SecLists
git clone https://github.com/danielmiessler/SecLists.git

# Use passwords as base patterns
python3 main.py test --wordlist SecLists/Passwords/Common-Credentials/10k-most-common.txt
```

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
├── pyproject.toml         # Project dependencies
├── .env.example           # Cookie configuration template
├── .env                   # Your cookies (git-ignored)
├── src/
│   ├── __init__.py
│   ├── wordlist.py        # Built-in patterns
│   ├── tester.py          # Core testing engine
│   ├── session.py         # Session & cookie management
│   ├── scraper.py         # Web scraping for wordlist generation
│   └── pattern_generator.py  # Pattern generation from scraped data
├── data/
│   └── custom.txt         # Custom patterns (optional)
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
- Security research on systems you own/have permission to test
- CTF challenges and competitions
- Authorized penetration testing

**Not for:**
- Unauthorized access attempts
- Fraud or theft
- Violating terms of service

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

- [x] **Generic Target URL Support** (v0.0.2)
  - Removed hardcoded darkprague.com
  - URL now required positional argument
  - Support any Pretix instance
  - Auto-adds https:// if missing

### Planned Features

- [ ] **Automated Wordlist Generation from Web Content**
  - Fetch event landing page
  - Crawl program/schedule for talk titles
  - Extract speaker names automatically
  - Generate targeted wordlist from scraped content
  - Output to `data/generated_wordlist.txt`

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

**TIXBUSTER** - Because sometimes the tickets just want to be free
