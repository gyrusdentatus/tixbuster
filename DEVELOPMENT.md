# TIXBUSTER Development Plan

**For the next Claude Code session or contributor**

This document outlines the implementation plan for the roadmap features listed in README.md.

---

## Feature 1: Automated Wordlist Generation from Web Content

### Requirements
- Fetch event landing page HTML
- Parse and extract speaker names, talk titles, sponsor names
- Generate voucher pattern combinations
- Save to `data/generated_wordlist.txt`

### Implementation Plan

#### Files to Create:
- `src/scraper.py` - Web scraping module
- `src/pattern_generator.py` - Pattern generation from scraped data

#### New CLI Command:
```bash
python3 main.py generate-wordlist https://event.example.com
```

#### Core Logic:

**src/scraper.py:**
```python
class EventScraper:
    def fetch_page(self, url):
        """Fetch HTML from event page"""

    def extract_speakers(self, html):
        """Extract speaker names from schedule/speakers page"""
        # Look for: <h3 class="speaker">, <div class="name">, etc.
        # Return: ["Alice Smith", "Bob Jones", ...]

    def extract_talks(self, html):
        """Extract talk/session titles"""
        # Return: ["Hacking the Mainframe", "Zero Trust Networks", ...]

    def extract_sponsors(self, html):
        """Extract sponsor names"""
        # Return: ["CompanyX", "CorporationY", ...]

    def crawl_schedule(self, base_url):
        """Follow links to /schedule, /speakers, /program"""
```

**src/pattern_generator.py:**
```python
class PatternGenerator:
    def generate_from_names(self, names):
        """
        Input: ["Alice Smith", "Bob Jones"]
        Output: [
            "ALICE", "ALICEGUEST", "ALICESMITH", "ASMITH",
            "BOB", "BOBGUEST", "BOBJONES", "BJONES",
            "ALICESMITHGUEST", "ALICESMITHFREE", ...
        ]
        """

    def generate_from_talks(self, titles):
        """
        Input: ["Hacking the Mainframe", "Zero Trust"]
        Output: [
            "HACKING", "MAINFRAME", "HACKINGMAINFRAME",
            "ZEROTRUST", "ZERO", "TRUST", ...
        ]
        """

    def add_common_suffixes(self, base_patterns):
        """Add GUEST, FREE, VIP, PASS, 2025, etc."""
```

#### Integration:
- Add to `main.py` as new subcommand `generate-wordlist`
- Save output to `data/generated_wordlist.txt`
- Automatically test with `python3 main.py test --wordlist data/generated_wordlist.txt`

#### Testing:
```bash
# Test with a real conference site
python3 main.py generate-wordlist https://darkprague.com

# Should output:
# [*] Fetching https://darkprague.com
# [*] Found 42 speakers
# [*] Found 73 talk titles
# [*] Found 8 sponsors
# [*] Generated 847 voucher patterns
# [*] Saved to data/generated_wordlist.txt
```

---

## Feature 2: Random Bruteforce Pattern Generation

### Requirements
- Generate random alphanumeric codes with configurable patterns
- Support prefix, suffix, or fully random modes
- Character sets: A-Z, a-z, 0-9 (configurable)
- CLI control over pattern length and count

### Implementation Plan

#### Files to Modify:
- `src/wordlist.py` - Add random generation functions
- `main.py` - Add `--random` flag and related options

#### Core Logic:

**src/wordlist.py:**
```python
import random
import string

def generate_random_codes(count=100, length=6, charset='upper', prefix='', suffix=''):
    """
    Generate random voucher codes

    Args:
        count: Number of codes to generate
        length: Code length (excluding prefix/suffix)
        charset: 'upper' (A-Z), 'lower' (a-z), 'alphanum' (A-Z,a-z,0-9), 'uppernumeric' (A-Z,0-9)
        prefix: Fixed prefix (e.g., 'DARK')
        suffix: Fixed suffix (e.g., '2025')

    Returns:
        List of random codes

    Examples:
        generate_random_codes(10, 6, 'upper', prefix='DARK')
        # ['DARK38YLKZ', 'DARKPPQRST', 'DARKMNBVCX', ...]

        generate_random_codes(10, 4, 'uppernumeric', suffix='FREE')
        # ['KK3DFREE', 'X9Y1FREE', '4ABCFREE', ...]

        generate_random_codes(5, 6, 'alphanum')
        # ['KkBdX1', 'Qq8Zz3', 'Mm2Pp7', ...]
    """
    charsets = {
        'upper': string.ascii_uppercase,
        'lower': string.ascii_lowercase,
        'alphanum': string.ascii_letters + string.digits,
        'uppernumeric': string.ascii_uppercase + string.digits
    }

    chars = charsets.get(charset, string.ascii_uppercase)
    codes = []

    for _ in range(count):
        random_part = ''.join(random.choices(chars, k=length))
        code = f"{prefix}{random_part}{suffix}"
        codes.append(code)

    return codes
```

#### CLI Integration:

**main.py test command additions:**
```python
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
```

**cmd_test() modification:**
```python
def cmd_test(args):
    # ... existing code ...

    if args.random:
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
```

#### Usage Examples:

```bash
# Generate 100 random 6-character codes (A-Z,0-9)
python3 main.py test --random 100

# Random codes with DARK prefix (like DARKABCD12)
python3 main.py test --random 50 --random-prefix DARK --random-length 6

# Random codes with FREE suffix (like KK3DFREE)
python3 main.py test --random 50 --random-suffix FREE --random-length 4

# Full random uppercase only (like KKBDXZ)
python3 main.py test --random 100 --random-charset upper --random-length 6

# Mixed case alphanumeric (like Kk8Bd3)
python3 main.py test --random 100 --random-charset alphanum --random-length 6

# Combo: prefix + random + suffix (like DARK38YL2025)
python3 main.py test --random 200 --random-prefix DARK --random-suffix 2025 --random-length 4
```

#### Smart Mode Integration:

**Add to src/wordlist.py:**
```python
def get_smart_random_patterns(base_patterns, variations=10):
    """
    Generate random variations of successful patterns

    If you found KATKA works but expired, try:
    - KATKA + random 2 digits: KATKA01, KATKA99
    - K + random 4 chars: KBDXZ, KPPQR
    - Random 2 + ATKA: 38ATKA, 99ATKA
    """
    smart_codes = []

    for pattern in base_patterns:
        # Add numeric suffixes
        for i in range(variations):
            smart_codes.append(f"{pattern}{random.randint(10,99)}")

        # Take first letter + random
        if len(pattern) > 0:
            first = pattern[0]
            for _ in range(variations):
                random_part = ''.join(random.choices(string.ascii_uppercase, k=4))
                smart_codes.append(f"{first}{random_part}")

    return smart_codes
```

#### Testing:
```bash
# Verify generation works
python3 -c "from src.wordlist import generate_random_codes; print(generate_random_codes(5, 6, 'uppernumeric', prefix='DARK'))"

# Should output something like:
# ['DARKAB12CD', 'DARK99ZZQQ', 'DARKPP88MM', ...]
```

---

## Feature 3: Multi-threading Support

### Requirements
- Replace single-threaded loop with ThreadPoolExecutor or asyncio
- Maintain per-thread rate limiting
- Preserve result aggregation
- Add `--threads N` CLI argument

### Implementation Plan

#### Files to Modify:
- `src/tester.py` - Add threading support
- `main.py` - Add `--threads` argument

#### Core Changes:

**src/tester.py:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class VoucherTester:
    def __init__(self, base_url, verbose=False, threads=1):
        self.threads = threads
        self.lock = threading.Lock()  # For shared state

    def test_batch_threaded(self, codes, session, csrf_token):
        """
        Multi-threaded batch testing
        """
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(
                    self.test_voucher,
                    code,
                    session,
                    csrf_token
                ): code for code in codes
            }

            for future in as_completed(futures):
                code = futures[future]
                status, detail = future.result()

                # Thread-safe result aggregation
                with self.lock:
                    self._update_results(code, status, detail)
```

**Key Considerations:**
- Each thread needs its own session (thread-local storage)
- Rate limiting per-thread: `time.sleep(0.5 / self.threads)`
- Progress bar updates must be thread-safe
- Graceful handling of Ctrl+C in threaded mode

#### CLI Integration:
```bash
# Single-threaded (default, safe)
python3 main.py test --priority

# 5 threads (faster)
python3 main.py test --priority --threads 5

# 10 threads (aggressive, risk of rate limiting)
python3 main.py test --priority --threads 10
```

#### Performance Targets:
- 1 thread: ~1.0 req/sec (baseline)
- 5 threads: ~4-5 req/sec
- 10 threads: ~8-9 req/sec (if not rate limited)

---

## Feature 4: WAF Detection & Adaptive Throttling

### Requirements
- Detect Cloudflare, Imperva, AWS WAF
- Monitor error patterns (403, 429, timeouts)
- Interactive prompt on throttling
- Auto-adjust thread count and delays
- Fallback to single-threaded mode

### Implementation Plan

#### Files to Create:
- `src/waf_detector.py` - WAF detection logic
- `src/throttle_manager.py` - Adaptive throttling

#### Core Logic:

**src/waf_detector.py:**
```python
class WAFDetector:
    def detect_waf(self, response):
        """
        Detect WAF from response headers and body
        """
        waf_signatures = {
            'cloudflare': ['cf-ray', 'cloudflare'],
            'imperva': ['incap_ses', 'visid_incap'],
            'aws': ['x-amzn-requestid'],
            'akamai': ['akamai-x-cache']
        }

        for waf, signatures in waf_signatures.items():
            for sig in signatures:
                if sig in response.headers or sig in response.text.lower():
                    return waf
        return None

    def is_throttled(self, response):
        """Detect throttling/blocking"""
        return (
            response.status_code in [403, 429, 503] or
            'challenge' in response.text.lower() or
            'blocked' in response.text.lower()
        )
```

**src/throttle_manager.py:**
```python
class ThrottleManager:
    def __init__(self):
        self.consecutive_errors = 0
        self.timeout_count = 0

    def should_prompt_user(self):
        """Decide if we should ask user to continue"""
        return (
            self.consecutive_errors >= 5 or
            self.timeout_count >= 10
        )

    def prompt_continue(self):
        """SQLmap-style prompt"""
        print("\n[!] Detected throttling/blocking")
        print("[!] Consecutive errors: {}".format(self.consecutive_errors))
        print("[!] Timeouts: {}".format(self.timeout_count))
        print("\n[?] Options:")
        print("    [C]ontinue with current settings")
        print("    [S]low down (reduce threads, increase delay)")
        print("    [A]bort")

        choice = input("\n[?] Continue? [c/S/a]: ").lower()
        return choice

    def adjust_settings(self, tester):
        """Auto-adjust based on errors"""
        if self.consecutive_errors >= 3:
            # Reduce threads by half
            tester.threads = max(1, tester.threads // 2)
            # Double the delay
            tester.base_delay *= 2
            print(f"[*] Adjusted: threads={tester.threads}, delay={tester.base_delay}s")
```

#### Integration into test_batch:
```python
def test_batch(self, codes, session, csrf_token):
    throttle_mgr = ThrottleManager()
    waf_detector = WAFDetector()

    for code in codes:
        try:
            status, detail = self.test_voucher(code, session, csrf_token)

            if status == 'ERROR':
                throttle_mgr.consecutive_errors += 1
            else:
                throttle_mgr.consecutive_errors = 0

        except Timeout:
            throttle_mgr.timeout_count += 1

        # Check if we should prompt
        if throttle_mgr.should_prompt_user():
            choice = throttle_mgr.prompt_continue()

            if choice == 'a':
                print("[!] Aborting...")
                break
            elif choice == 's':
                throttle_mgr.adjust_settings(self)
            # 'c' or default: continue as-is
```

---

## Feature 5: Pretix Permission Enumeration

### Requirements
- Read Pretix permission model docs
- Test for permission bypass vulnerabilities
- Enumerate accessible API endpoints
- Detect structural misconfigurations

### Implementation Plan

#### Files to Create:
- `src/pretix_enum.py` - Pretix-specific enumeration
- `src/api_fuzzer.py` - API endpoint discovery

#### Documentation Review:
1. https://docs.pretix.eu/dev/development/implementation/permissions.html
2. https://docs.pretix.eu/dev/development/structure.html
3. https://docs.pretix.eu/dev/api/

#### Core Tests:

**Permission Tests:**
```python
class PretixEnumerator:
    def test_unauthenticated_access(self):
        """Test API endpoints without auth"""
        endpoints = [
            '/api/v1/organizers/',
            '/api/v1/events/',
            '/control/events/',
        ]

    def test_permission_escalation(self):
        """Test for horizontal/vertical privilege escalation"""

    def test_object_level_auth(self):
        """Test IDOR vulnerabilities"""

    def enumerate_permissions(self):
        """List all available permissions from docs"""
        # can_view_orders, can_change_orders, etc.
```

**Structural Tests:**
```python
class PretixStructureChecker:
    def check_csrf_protection(self):
        """Verify CSRF tokens are enforced"""

    def check_cors_config(self):
        """Test CORS misconfigurations"""

    def check_rate_limiting(self):
        """Identify rate limit thresholds"""

    def check_debug_mode(self):
        """Detect if debug mode is exposed"""
```

#### New CLI Command:
```bash
# Enumerate permissions and misconfigs
python3 main.py enum https://tix.example.com

# Output:
# [*] Enumerating Pretix instance: https://tix.example.com
# [+] Found public API endpoints: 12
# [!] Unauthenticated access to: /api/v1/organizers/
# [!] CORS misconfiguration detected
# [+] Rate limit: ~100 req/min
# [*] Checking voucher endpoint permissions...
```

---

## Testing Strategy

### For Each Feature:

1. **Unit Tests** (`tests/test_*.py`):
   ```bash
   pytest tests/test_scraper.py
   pytest tests/test_threading.py
   pytest tests/test_waf_detector.py
   pytest tests/test_pretix_enum.py
   ```

2. **Integration Tests**:
   - Test against a local Pretix instance (Docker)
   - Use test vouchers with known responses

3. **Manual Testing**:
   - Real-world conference site testing
   - Rate limit validation
   - WAF detection accuracy

---

## Development Environment Setup

```bash
# Clone repo
git clone https://github.com/gyrusdentatus/tixbuster.git
cd tixbuster

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install requests beautifulsoup4 pytest

# Run tests
pytest -v

# Test locally
python3 main.py validate
python3 main.py test --priority --threads 5
```

---

## Contribution Guidelines

1. **Branch naming**: `feature/web-scraping`, `feature/threading`, etc.
2. **Commit messages**: Follow existing pattern (`SHIT:`, `FIX:`, `FEAT:`)
3. **Code style**: Follow existing patterns (no linters enforced)
4. **Testing**: Add tests for new features
5. **Documentation**: Update README.md with new CLI commands

---

---

## Questions for Implementation

- **Threading**: Use `ThreadPoolExecutor` or `asyncio`? (ThreadPoolExecutor simpler)
- **Web Scraping**: BeautifulSoup or regex? (BS4 more robust)
- **WAF Detection**: How aggressive should auto-throttling be?
- **Pretix Enum**: Should this be a separate tool or integrated?

---

**Ready to build? Fork, branch, and PR! 🚀**
