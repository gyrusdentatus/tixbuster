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
        """Extract speaker names from HTML and plain text"""
        speakers = []

        # Noise keywords to filter out (navigation, UI, generic terms)
        noise_keywords = [
            'menu', 'login', 'logout', 'register', 'tickets', 'schedule', 'speakers',
            'sessions', 'filter', 'home', 'about', 'contact', 'twitter', 'telegram',
            'discord', 'github', 'medium', 'youtube', 'linkedin', 'facebook',
            'get tickets', 'buy now', 'learn more', 'read more', 'click here',
            'newsletter', 'subscribe', 'follow us', 'join us', 'sign up',
            'cookie policy', 'privacy policy', 'terms', 'conditions', 'previous years',
            'organized by', 'sponsored by', 'partners', 'connect', 'get in touch',
            'media partnerships', 'contact email', 'closing ceremony', 'opening ceremony'
        ]

        # Common patterns for speaker names in HTML
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
                # Filter: must look like a name, not noise
                if (len(name) > 3 and len(name) < 50 and ' ' in name and
                    not any(keyword in name.lower() for keyword in noise_keywords)):
                    speakers.append(name)

        # Extract from plain text (browser copy/paste, terminal schedules)
        # Strip ANSI codes first
        text_only = re.sub(r'\x1b\[[0-9;]*m', '', html)

        # Look for standalone name lines (2-4 capitalized words max, short)
        # This avoids matching talk titles which are usually longer
        lines = text_only.split('\n')
        # Particles that can be lowercase in names
        name_particles = {'de', 'van', 'von', 'der', 'den', 'del', 'la', 'le', 'di', 'da'}

        for line in lines:
            line = line.strip()
            # Must be 2-4 words, mostly capitalized, total length 8-40 chars
            words = line.split()
            if (2 <= len(words) <= 4 and
                8 <= len(line) <= 40 and
                not re.match(r'^\d{1,2}:\d{2}', line) and  # Not a timestamp
                not any(keyword in line.lower() for keyword in noise_keywords)):
                # Check if mostly capitalized (allows particles like "de", "van")
                cap_words = [w for w in words if w and (w[0].isupper() or w.lower() in name_particles)]
                if len(cap_words) >= len(words) - 1:  # Allow 1 non-cap word (particle)
                    speakers.append(line)

        # Deduplicate
        speakers = list(set(speakers))

        if self.verbose:
            print(f"[SPEAKERS] Found {len(speakers)} unique speakers")

        return speakers

    def extract_talks(self, html):
        """Extract talk/session titles from HTML and plain text"""
        talks = []

        # Noise to filter out (UI elements, navigation, generic text)
        noise_keywords = [
            'menu', 'login', 'logout', 'register', 'tickets', 'schedule', 'speakers',
            'sessions', 'filter', 'home', 'about', 'contact', 'twitter', 'telegram',
            'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'sustainable futures', 'core & evm', 'developer ecosystem', 'impact defi',
            'societal challenges', 'root', 'flower', 'seed', 'workshop',
            'min', 'opening ceremony', 'closing ceremony', 'fireside chat',
            'get tickets', 'buy now', 'previous years', 'organized by', 'sponsored by',
            'get in touch', 'contact email'
        ]

        # Common patterns for talk titles in HTML
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
                # Filter: substantial text, not noise
                if (len(title) > 10 and len(title) < 200 and
                    not any(keyword in title.lower() for keyword in noise_keywords) and
                    not re.match(r'^\d{1,2}:\d{2}', title)):  # Not a timestamp
                    talks.append(title)

        # Extract from plain text - look for talk titles (longer phrases, not all caps)
        text_only = re.sub(r'\x1b\[[0-9;]*m', '', html)
        lines = text_only.split('\n')

        # Track potential speaker names to exclude them from talks
        name_particles = {'de', 'van', 'von', 'der', 'den', 'del', 'la', 'le', 'di', 'da'}
        potential_speakers = set()
        for line in lines:
            line = line.strip()
            words = line.split()
            # If it looks like a name (2-4 mostly capitalized words, short), mark it
            if 2 <= len(words) <= 4 and 8 <= len(line) <= 40:
                cap_words = [w for w in words if w and (w[0].isupper() or w.lower() in name_particles)]
                if len(cap_words) >= len(words) - 1:
                    potential_speakers.add(line.lower())

        for line in lines:
            line = line.strip()
            # Potential talk title: 15-150 chars, has multiple words, not all caps, not timestamps
            # AND not a speaker name
            if (15 <= len(line) <= 150 and
                ' ' in line and
                not line.isupper() and
                not re.match(r'^\d{1,2}:\d{2}', line) and
                line.lower() not in potential_speakers and
                not any(keyword in line.lower() for keyword in noise_keywords)):
                talks.append(line)

        # Deduplicate and clean
        unique_talks = []
        seen = set()
        for talk in talks:
            clean = ' '.join(talk.split())  # Normalize whitespace
            if clean and clean.lower() not in seen:
                seen.add(clean.lower())
                unique_talks.append(clean)

        if self.verbose:
            print(f"[TALKS] Found {len(unique_talks)} unique talk titles")

        return unique_talks

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
