"""
Web scraping module for TIXBUSTER
Extracts speaker names, talk titles, and sponsors from event pages
"""

import requests
import re
from urllib.parse import urljoin, urlparse


class EventScraper:
    """Scrape event websites for voucher code hints"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_page(self, url):
        """Fetch HTML from URL"""
        try:
            if self.verbose:
                print(f"[FETCH] {url}")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if self.verbose:
                print(f"[ERROR] Failed to fetch {url}: {e}")
            return None

    def extract_speakers(self, html):
        """Extract speaker names from HTML"""
        speakers = []

        # Common patterns for speaker names
        patterns = [
            r'<h[1-6][^>]*class="[^"]*speaker[^"]*"[^>]*>([^<]+)</h[1-6]>',
            r'<div[^>]*class="[^"]*speaker[^"]*"[^>]*>([^<]+)</div>',
            r'<span[^>]*class="[^"]*name[^"]*"[^>]*>([^<]+)</span>',
            r'<p[^>]*class="[^"]*speaker[^"]*"[^>]*>([^<]+)</p>',
            # Pretalx-style schedule
            r'<h3[^>]*>([A-Z][a-z]+\s+[A-Z][a-z]+)</h3>',
            # Name followed by title/company
            r'<strong>([A-Z][a-z]+\s+[A-Z][a-z]+)</strong>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                name = match.strip()
                # Filter out noise (must look like a name)
                if len(name) > 3 and len(name) < 50 and ' ' in name:
                    speakers.append(name)

        # Also extract from plain text (for terminal-rendered schedules like Pretalx)
        # Look for capitalized names in format "FirstName LastName" without HTML tags
        # Strip ANSI codes first
        text_only = re.sub(r'\x1b\[[0-9;]*m', '', html)
        name_pattern = r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,})\b'
        text_matches = re.findall(name_pattern, text_only)
        for match in text_matches:
            if len(match) > 5 and len(match) < 50:
                speakers.append(match.strip())

        # Deduplicate
        speakers = list(set(speakers))

        if self.verbose:
            print(f"[SPEAKERS] Found {len(speakers)} unique speakers")

        return speakers

    def extract_talks(self, html):
        """Extract talk/session titles from HTML"""
        talks = []

        # Common patterns for talk titles
        patterns = [
            r'<h[1-6][^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</h[1-6]>',
            r'<div[^>]*class="[^"]*session[^"]*title[^"]*"[^>]*>([^<]+)</div>',
            r'<a[^>]*class="[^"]*talk[^"]*"[^>]*>([^<]+)</a>',
            # Pretalx schedule format
            r'<h4[^>]*>([^<]{10,})</h4>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                title = match.strip()
                # Filter: must be substantial text
                if len(title) > 5 and len(title) < 200:
                    talks.append(title)

        # Deduplicate
        talks = list(set(talks))

        if self.verbose:
            print(f"[TALKS] Found {len(talks)} unique talk titles")

        return talks

    def extract_sponsors(self, html):
        """Extract sponsor names from HTML"""
        sponsors = []

        # Common patterns for sponsors
        patterns = [
            r'<div[^>]*class="[^"]*sponsor[^"]*"[^>]*>([^<]+)</div>',
            r'<h[1-6][^>]*class="[^"]*sponsor[^"]*"[^>]*>([^<]+)</h[1-6]>',
            r'<img[^>]*alt="([^"]*sponsor[^"]*)"',
            r'<a[^>]*class="[^"]*sponsor[^"]*"[^>]*>([^<]+)</a>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                name = match.strip()
                # Filter: must look like a company name
                if len(name) > 2 and len(name) < 50:
                    sponsors.append(name)

        # Deduplicate
        sponsors = list(set(sponsors))

        if self.verbose:
            print(f"[SPONSORS] Found {len(sponsors)} unique sponsors")

        return sponsors

    def find_subpages(self, base_url, html):
        """Find schedule/speaker/program subpages"""
        subpages = []

        # Common subpage patterns
        keywords = ['schedule', 'speakers', 'program', 'agenda', 'talks', 'sessions']

        # Extract all links
        links = re.findall(r'<a[^>]*href="([^"]+)"', html)

        for link in links:
            link_lower = link.lower()
            for keyword in keywords:
                if keyword in link_lower:
                    full_url = urljoin(base_url, link)
                    if full_url not in subpages:
                        subpages.append(full_url)
                    break

        if self.verbose:
            print(f"[SUBPAGES] Found {len(subpages)} related pages")

        return subpages

    def crawl_event(self, base_url, max_depth=2):
        """
        Crawl event website for all relevant data

        Args:
            base_url: Event homepage URL
            max_depth: How many levels deep to crawl (1 = main page only)

        Returns:
            dict with speakers, talks, sponsors lists
        """
        all_speakers = []
        all_talks = []
        all_sponsors = []
        visited = set()

        def crawl_page(url, depth):
            if depth > max_depth or url in visited:
                return

            visited.add(url)
            html = self.fetch_page(url)

            if not html:
                return

            # Extract data
            all_speakers.extend(self.extract_speakers(html))
            all_talks.extend(self.extract_talks(html))
            all_sponsors.extend(self.extract_sponsors(html))

            # Find subpages to crawl
            if depth < max_depth:
                subpages = self.find_subpages(url, html)
                for subpage in subpages[:5]:  # Limit to 5 subpages per level
                    crawl_page(subpage, depth + 1)

        print(f"[*] Crawling {base_url}...")
        crawl_page(base_url, 1)

        # Deduplicate final results
        results = {
            'speakers': list(set(all_speakers)),
            'talks': list(set(all_talks)),
            'sponsors': list(set(all_sponsors))
        }

        print(f"[*] Crawl complete:")
        print(f"    - {len(results['speakers'])} speakers")
        print(f"    - {len(results['talks'])} talks")
        print(f"    - {len(results['sponsors'])} sponsors")

        return results
