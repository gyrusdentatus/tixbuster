# TIXBUSTER

**Generic voucher code bruteforcer for Pretix ticketing systems**

Systematically tests voucher codes against Pretix-based ticket platforms with rate limiting, session validation, and intelligent pattern generation.

## Features

- 🎯 **2,151+ built-in patterns** from common voucher naming conventions
- 🔒 **Session validation** with control test
- ⚡ **Rate limiting protection** with adaptive delays
- 🔍 **Multiple search modes** (priority, full scan, custom wordlist)
- 📊 **Detailed statistics** and result categorization
- 🛡️ **Cloudflare detection** and handling

## Quick Start

```bash
# 1. Update cookies in src/session.py
# 2. Validate session
python3 main.py validate

# 3. Test priority codes (36 highest probability)
python3 main.py test --priority

# 4. Test all patterns (~1 hour for 2151 codes)
python3 main.py test --all
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
# Priority codes only (~2-3 minutes)
python3 main.py test --priority

# All patterns (~60-90 minutes)
python3 main.py test --all

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

- **Priority codes**: ~2-3 minutes (36 codes)
- **Full scan**: ~60-90 minutes (2,151 codes)
- **Rate**: ~0.5-1.0 requests/second (adaptive)
- **Memory**: < 50MB

## Strategy Tips

1. Start with priority codes (highest probability)
2. Monitor for EXPIRED codes (indicates valid format)
3. Use --verbose to understand response patterns
4. Check UNKNOWN responses manually
5. Add successful patterns to custom wordlist

## Ethical Usage

This tool is for:
- ✅ Security research on systems you own/have permission to test
- ✅ CTF challenges and competitions
- ✅ Authorized penetration testing

**Not for:**
- ❌ Unauthorized access attempts
- ❌ Fraud or theft
- ❌ Violating terms of service

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
