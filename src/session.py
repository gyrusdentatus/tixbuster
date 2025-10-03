"""
Session and cookie management for TIXBUSTER
"""

import requests
import sys


class SessionManager:
    """Manages HTTP session, cookies, and CSRF tokens"""

    # Default cookies (update these from your browser)
    DEFAULT_COOKIES = {
        '__Host-pretix_csrftoken': 'D0k1wkhR0rsDxYyglTCsjThPEfnlwHB8',
        '__Host-pretix_session': 'sq0i3grzzl0qx5syby8fp0g2pal9y1k7',
        'cf_clearance': 'FzhHpo50AKGs3VElxkloWnVPsQoIyzHJfJZettUxhx8-1759455892-1.2.1.1-k2IUVTJEHB7bT4eWhvBpKzX58EbXUmwD3vDp3FSvZMpyHjVZioROy.p9g5ZonDsyd6.YkGiCYWygkmHnA3gJOX1o3DTdVh8A5_ABECHvCedsDTx1qwQMJ55aARofi5Af84zYm5z4tPFMTyEzgjdpTiFf1_rGL.xJBWM2MpIEOoWn.3BJuZBrirCb2oCNvx2TNtQ1Oq1FgQ2Yk5qev8_G3W81NZWYbyyQpVLf_5WJTjU'
    }

    DEFAULT_CSRF = 'vx5XaRivcrf40vwzmkjXuWzXhqxmNxlkYnfOw1pc2IxxnjUFx3LfDFGCLvKx94Mi'

    def __init__(self, base_url="https://tix.darkprague.com", cookies=None, csrf_token=None, verbose=False):
        self.base_url = base_url
        self.cookies = cookies or self.DEFAULT_COOKIES.copy()
        self.csrf_token = csrf_token or self.DEFAULT_CSRF
        self.verbose = verbose
        self.session = None

    def create_session(self):
        """Create and configure HTTP session"""
        session = requests.Session()

        # Set headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/'
        })

        # Set cookies
        session.cookies.update(self.cookies)

        self.session = session
        return session

    def validate_session(self):
        """
        Validate session by testing IMDARK control voucher
        Returns: (success: bool, message: str)
        """
        print("[CONTROL] Testing IMDARK voucher to validate session...")

        # Show cookie info (truncated for security)
        if self.verbose:
            print(f"[COOKIES] csrf: {self.cookies.get('__Host-pretix_csrftoken', '')[:10]}... " +
                  f"session: {self.cookies.get('__Host-pretix_session', '')[:10]}... " +
                  f"cf: {self.cookies.get('cf_clearance', '')[:10]}...")

        # Create session if not exists
        if not self.session:
            self.create_session()

        try:
            # Import here to avoid circular dependency
            try:
                from .tester import VoucherTester
            except ImportError:
                # When running as standalone script
                from tester import VoucherTester

            tester = VoucherTester(self.base_url, self.verbose)
            status, detail = tester.test_voucher('IMDARK', self.session, self.csrf_token)

            if status == 'EXPIRED':
                print("[CONTROL] ✓ IMDARK returned 'expired' - cookies valid!")
                if self.verbose and detail:
                    print(f"[CONTROL] UUID: {detail}")
                return True, "Session valid"

            elif status in ['ERROR', 'EXCEPTION']:
                print(f"[CONTROL] ✗ Session invalid or network error: {detail}")
                print("[CONTROL] Exiting - please refresh your cookies")
                return False, f"Session error: {detail}"

            else:
                print(f"[CONTROL] ⚠ Unexpected response: {status}")
                print(f"[CONTROL] Detail: {detail}")
                print("[CONTROL] Continuing anyway, but session might be invalid...")
                return True, f"Unexpected response: {status}"

        except Exception as e:
            print(f"[CONTROL] ✗ Exception during control test: {e}")
            print("[CONTROL] Exiting - please check your connection")
            return False, f"Exception: {e}"

    def update_cookies(self, cookies_dict):
        """Update cookies (e.g., from fresh browser session)"""
        self.cookies.update(cookies_dict)
        if self.session:
            self.session.cookies.update(cookies_dict)

    def update_csrf_token(self, csrf_token):
        """Update CSRF token"""
        self.csrf_token = csrf_token

    def get_session_info(self):
        """Get current session information"""
        return {
            'base_url': self.base_url,
            'cookies': {k: v[:10] + '...' for k, v in self.cookies.items()},
            'csrf_token': self.csrf_token[:10] + '...',
            'session_active': self.session is not None
        }


def validate_and_exit_if_invalid(session_manager):
    """
    Validate session and exit if invalid
    Convenience function for scripts
    """
    success, message = session_manager.validate_session()
    if not success:
        print(f"\n[!] Validation failed: {message}")
        print("[!] Update your cookies and try again")
        sys.exit(1)
    return session_manager.session


if __name__ == "__main__":
    # Test session validation when run directly
    print("=" * 60)
    print("SESSION VALIDATOR")
    print("=" * 60)

    manager = SessionManager(verbose=True)
    success, message = manager.validate_session()

    print("\n" + "=" * 60)
    if success:
        print("✓ Session is VALID")
    else:
        print("✗ Session is INVALID")
    print(f"Message: {message}")
    print("=" * 60)

    sys.exit(0 if success else 1)
