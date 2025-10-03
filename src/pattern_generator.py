"""
Pattern generation module for TIXBUSTER
Converts scraped event data into voucher code patterns
"""

import re


class PatternGenerator:
    """Generate voucher patterns from scraped event data"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.common_suffixes = [
            '', 'GUEST', 'FREE', 'VIP', 'PASS', 'TICKET',
            '2025', '2024', 'DISCOUNT', 'PROMO', 'CODE'
        ]

    def generate_from_names(self, names):
        """
        Generate voucher patterns from person names

        Input: ["Alice Smith", "Bob Jones", "Dr. Jane Doe"]
        Output: [
            "ALICE", "ALICEGUEST", "ALICESMITH", "ASMITH",
            "BOB", "BOBGUEST", "BOBJONES", "BJONES",
            "JANE", "JANEGUEST", "JANEDOE", "JDOE",
            ...
        ]
        """
        patterns = []

        for name in names:
            # Clean up name (remove titles, special chars)
            name = re.sub(r'^(Dr|Mr|Ms|Mrs|Prof)\.?\s+', '', name, flags=re.IGNORECASE)
            name = re.sub(r'[^a-zA-Z\s]', '', name)
            parts = name.strip().split()

            if not parts:
                continue

            # First name variations
            if len(parts) >= 1:
                first = parts[0].upper()
                patterns.append(first)

                # First name + common suffixes
                for suffix in ['GUEST', 'FREE', 'VIP']:
                    patterns.append(f"{first}{suffix}")

            # Full name (no spaces)
            if len(parts) >= 2:
                fullname = ''.join(parts).upper()
                patterns.append(fullname)

                # First + Last
                first = parts[0].upper()
                last = parts[-1].upper()
                patterns.append(f"{first}{last}")

                # First initial + Last
                patterns.append(f"{first[0]}{last}")

                # Fullname + suffix
                for suffix in ['GUEST', 'FREE']:
                    patterns.append(f"{fullname}{suffix}")

            # Last name alone
            if len(parts) >= 2:
                last = parts[-1].upper()
                patterns.append(last)

        if self.verbose:
            print(f"[PATTERNS] Generated {len(patterns)} patterns from {len(names)} names")

        return list(set(patterns))  # Deduplicate

    def generate_from_talks(self, titles):
        """
        Generate voucher patterns from talk titles

        Input: ["Hacking the Mainframe", "Zero Trust Networks", "CTF Writeups"]
        Output: [
            "HACKING", "MAINFRAME", "HACKINGMAINFRAME",
            "ZERO", "TRUST", "ZEROTRUST", "NETWORKS",
            "CTF", "WRITEUPS", "CTFWRITEUPS",
            ...
        ]
        """
        patterns = []

        for title in titles:
            # Clean up title
            title = re.sub(r'[^a-zA-Z\s]', '', title)
            words = [w.upper() for w in title.split() if len(w) > 2]

            if not words:
                continue

            # Individual words
            patterns.extend(words)

            # Compound words (first 2-3 words together)
            if len(words) >= 2:
                patterns.append(''.join(words[:2]))

            if len(words) >= 3:
                patterns.append(''.join(words[:3]))

            # Words + suffixes
            for word in words[:3]:  # Only top 3 words
                for suffix in ['GUEST', 'PASS', 'VIP']:
                    patterns.append(f"{word}{suffix}")

        if self.verbose:
            print(f"[PATTERNS] Generated {len(patterns)} patterns from {len(titles)} talks")

        return list(set(patterns))  # Deduplicate

    def generate_from_sponsors(self, sponsors):
        """
        Generate voucher patterns from sponsor names

        Input: ["TechCorp Inc.", "Cyber Systems", "ACME Ltd"]
        Output: [
            "TECHCORP", "TECHCORPGUEST", "TECHCORPFREE",
            "CYBER", "SYSTEMS", "CYBERSYSTEMS",
            "ACME", "ACMEGUEST",
            ...
        ]
        """
        patterns = []

        for sponsor in sponsors:
            # Clean up sponsor name (remove Inc., Ltd, LLC, etc.)
            sponsor = re.sub(r'\s+(Inc|Ltd|LLC|Corp|GmbH|SA|SRL)\.?$', '', sponsor, flags=re.IGNORECASE)
            sponsor = re.sub(r'[^a-zA-Z\s]', '', sponsor)
            words = [w.upper() for w in sponsor.split() if len(w) > 1]

            if not words:
                continue

            # First word
            patterns.append(words[0])

            # Full company name (no spaces)
            if len(words) >= 2:
                fullname = ''.join(words)
                patterns.append(fullname)

            # Company name + suffixes
            for word in words[:2]:
                for suffix in ['GUEST', 'FREE', 'VIP', 'SPONSOR']:
                    patterns.append(f"{word}{suffix}")

        if self.verbose:
            print(f"[PATTERNS] Generated {len(patterns)} patterns from {len(sponsors)} sponsors")

        return list(set(patterns))  # Deduplicate

    def add_common_variations(self, base_patterns):
        """
        Add common variations to existing patterns

        Input: ["HACKER"]
        Output: [
            "HACKER", "HACKERGUEST", "HACKERFREE", "HACKERVIP",
            "HACKER2025", "HACKER2024", "HACKERPASS", ...
        ]
        """
        variations = []

        for pattern in base_patterns:
            # Original
            variations.append(pattern)

            # Add suffixes
            for suffix in self.common_suffixes:
                if suffix:  # Skip empty suffix
                    variations.append(f"{pattern}{suffix}")

        if self.verbose:
            print(f"[VARIATIONS] Expanded {len(base_patterns)} patterns to {len(variations)}")

        return list(set(variations))

    def generate_all(self, scraped_data, include_variations=True):
        """
        Generate all patterns from scraped data

        Args:
            scraped_data: dict with 'speakers', 'talks', 'sponsors' keys
            include_variations: Add common suffix variations

        Returns:
            List of unique voucher code patterns
        """
        all_patterns = []

        # Generate from speakers
        if scraped_data.get('speakers'):
            speaker_patterns = self.generate_from_names(scraped_data['speakers'])
            all_patterns.extend(speaker_patterns)
            print(f"[*] Speaker patterns: {len(speaker_patterns)}")

        # Generate from talks
        if scraped_data.get('talks'):
            talk_patterns = self.generate_from_talks(scraped_data['talks'])
            all_patterns.extend(talk_patterns)
            print(f"[*] Talk patterns: {len(talk_patterns)}")

        # Generate from sponsors
        if scraped_data.get('sponsors'):
            sponsor_patterns = self.generate_from_sponsors(scraped_data['sponsors'])
            all_patterns.extend(sponsor_patterns)
            print(f"[*] Sponsor patterns: {len(sponsor_patterns)}")

        # Deduplicate base patterns
        all_patterns = list(set(all_patterns))
        print(f"[*] Base patterns (deduplicated): {len(all_patterns)}")

        # Add variations
        if include_variations:
            all_patterns = self.add_common_variations(all_patterns)
            print(f"[*] Total patterns with variations: {len(all_patterns)}")

        return sorted(all_patterns)
