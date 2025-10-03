"""
Master Wordlist for TIXBUSTER
Generic voucher patterns for Pretix ticketing systems
"""

import base64
import os


def get_katka_patterns():
    """KATKA patterns - @kk telegram handle, KATKAGUEST worked 2024"""
    return [
        'KATKA', 'KATKAGUEST', 'KATKA2025', 'KATKA2024',
        'KK', 'KKGUEST', 'KK2025', 'KK2024',
        'KATKAFREE', 'KKFREE', 'KATKAVIP', 'KKVIP',
        'KATKADARK', 'KKDARK', 'KATKAPRAGUE', 'KKPRAGUE',
        'KATKA25', 'KK25', 'KATKACTF', 'KKCTF',
        'KATKADARK2025', 'KKDARK2025', 'DARKKATKA', 'DARKKK',
        'KATKASC', 'KKSC', 'SCKATKA', 'SCKK',
        'SECONDKATKA', 'SECONDKK', 'CULTUREKK', 'CULTUREKATKA'
    ]


def get_punk_movement_patterns():
    """Punk movements - lunarpunk, cypherpunk, solarpunk"""
    movements = ['LUNARPUNK', 'CYPHERPUNK', 'SOLARPUNK', 'CRYPTOPUNK', 'ANALOGCYPHERPUNK']
    suffixes = ['', '25', '2025', '2024', 'FREE', 'GUEST', 'VIP', 'PASS', 'CTF']

    patterns = []
    for movement in movements:
        for suffix in suffixes:
            patterns.append(f"{movement}{suffix}")

    return patterns


def get_talk_event_patterns():
    """Talk titles and event names from schedule"""
    return [
        # DarkFi and key projects
        'DARKFI', 'DARKFIGUEST', 'DARKFIFREE', 'GLOWIES', 'DARKFIKIILLSGLOWIES',

        # Network States & Pop-up cities
        'NETWORKSTATES', 'POPUPCITIES', 'REFUGIO', 'MURAR', 'OPTING', 'OPTINGOUT',

        # Tools and projects
        'DISOBAY', 'DISSENSUS', 'DARKFOREST', 'MESHTASTIC', 'TOLLGATE', 'NYMVPN',
        'BITAXE', 'GAMMA601', 'BITAXEGAMMA', 'FHE', 'FOSS', 'XZ', 'XZUTILS',

        # Philosophy & Society
        'AGENTIC', 'AGENTICSOCIETY', 'HOLYWAR', 'TECHHOLYWAR', 'GENOCIDE',
        'MORALCOURAGE', 'COURAGE', 'SOVEREIGNTY', 'FREEDOM',

        # Finance & Crypto
        'DEFI', 'BANKSTERS', 'DEFYTHEBANKSTERS', 'ECASH', 'ZCASH20',
        'DASHDAO', 'LOGOS', 'LOGOSCIRCLE',

        # Privacy & Surveillance
        'SURVEILLANCE', 'ANONYMITY', 'WARMACHINE', 'SIGNALS', 'PERMISSIONLESS',
        'VERIFIABLE', 'SELFSO VEREIGN', 'ROOMS', 'ROOMSWITHOUTPERMISSION',

        # Biology tracks
        'BIOS', 'BIOHACKER', 'IMMORTALITY', 'GENES', 'AGEING',
        'NEUROBIOLOGY', 'CHOLESTEROL', 'DARKNET', 'WARONDRUGS',

        # Technical/Infrastructure
        'SPLINTERNETS', 'CDNS', 'DIGITALIDENTITY', 'SMARTCONTRACTS',
        'HOMEMINING', 'LOTTERY', 'MESHTASTICPARTY',

        # Critical themes
        'BLACKOUT', 'SURVIVING', 'EXILE', 'RUNNING', 'DIGITALHILLS',
        'CYPHERPUNKSTACK', 'VERIFIABLEOID'
    ]


def get_speaker_patterns():
    """All speakers from schedule + darkprague.com"""
    speakers = {
        # Main keynote speakers
        'GAVIN': ['GAVINWOOD', 'WOOD'],
        'CODY': ['CODYWILSON', 'WILSON'],
        'AMIR': ['AMIRTAAKI', 'TAAKI'],
        'HARRY': ['HARRYHALPIN', 'HALPIN'],
        'JARRAD': ['JARRADHOPE', 'HOPE'],

        # Schedule speakers (alphabetical)
        'ANN': ['ANNBRODY', 'BRODY'],
        'ELENA': ['ELENAGROZDANOVSKA', 'GROZDANOVSKA'],
        'MICHAL': ['MICHALKODNAR', 'KODNAR', 'MICHALALTAIR', 'ALTAIR'],
        'NAOMIII': [],
        'SHIRLY': ['SHIRLYVALGE', 'VALGE'],
        'CASEY': ['CASEYCARR', 'CARR'],
        'ESHEL': [],
        'JOSH': ['JOSHDATKO', 'DATKO'],
        'SILKE': ['SILKENOA', 'NOA'],
        'JURAJ': [],
        'OLGA': ['OLGAUKOLOVA', 'UKOLOVA'],
        'GRACE': ['GRACERACHMANY', 'RACHMANY'],
        'RENE': ['RENEMALMGREN', 'MALMGREN'],
        'BOB': ['BOBSUMMERWILL', 'SUMMERWILL'],
        'SVEN': ['SVENWELSCH', 'WELSCH'],
        'ROBIN': ['ROBINTHATCHER', 'THATCHER'],
        'RACHEL': ['RACHELROSE', 'OLEARY'],
        'RAY': ['RAYYOUSSEF', 'YOUSSEF'],
        'TOMASZ': ['TOMASZMENTZEN', 'MENTZEN'],
        'TOMAS': ['TOMASS', 'TOMASSTUDENIK', 'STUDENIK'],
        'ELSIRION': [],
        'FRANK': ['FRANKBRAUN', 'BRAUN'],
        'KARO': ['KAROZAGORUS', 'ZAGORUS'],
        'FERENC': ['FERENCKOVACS', 'KOVACS'],
        'MIDEG': ['MIDEGDUGAROVA', 'DUGAROVA'],
        'VACLAV': ['VACLAVPAVLIN', 'PAVLIN'],
        'PAVOL': ['PAVOLLUPTAK', 'LUPTAK'],
        'MATTHIAS': ['MATTHIASTARASIEWICZ', 'TARASIEWICZ'],
        'EXILEDSURFER': [],
        'SHADOWSHIELD': [],
        'BOGOMIL': ['BOGOMILSHOPOV'],
        'KETOMINER': [],
        'ROOS': [],
        'DLLUD': [],
        'DAVE': ['DAVESTANN', 'STANN'],
        'SERINKO': [],
        'NOGOODKID': [],
        'RYAN': ['RYANLACKEY', 'LACKEY'],
        'ZOE': ['ZOECORMIER', 'CORMIER'],
        'TAL': ['TALEPHRAT', 'EPHRAT'],
        'DARKO': [],
        'POLTO': [],
        'DARO': [],
        'KRIS': [],
        'PAVEL': ['PAVELKUBU', 'KUBU'],
        'JAN': [],
        'THATPRIVACYGIRL': ['THATPRIVGIRL', 'PRIVACYGIRL']
    }

    patterns = []
    suffixes = ['', 'GUEST', 'FREE', 'VIP', 'PASS', '2025', '25']

    for base, variants in speakers.items():
        names = [base] + variants
        for name in names:
            for suffix in suffixes:
                patterns.append(f"{name}{suffix}")

    return list(set(patterns))


def get_sponsor_patterns():
    """Sponsors and partners from darkprague.com"""
    sponsors = ['BITOMAT', 'CAKE', 'CAKEWALLET', 'KUSAMA', 'ZCASH', 'FEDIMINT', 'LOGOS']
    suffixes = ['', 'FREE', 'GUEST', 'VIP', 'PASS', '2025', '25']

    patterns = []
    for sponsor in sponsors:
        for suffix in suffixes:
            patterns.append(f"{sponsor}{suffix}")

    return patterns


def get_venue_event_patterns():
    """Venue and event-specific codes"""
    return [
        # Venue
        'SECONDCULTURE', 'SECOND', 'CULTURE', '2NDCULTURE', '2CULTURE',
        'SCFREE', 'SCGUEST', 'SCVIP', 'SCPASS', 'SC2025', 'SC25',

        # Dark Prague
        'DARKPRAGUE', 'DARKPRAGUE25', 'DARKPRAGUE2025', 'DARK2025',
        'PRAGUEDARK', 'PRAHA2025', 'PRAGUE2025', 'DP2025', 'DP25',
        'DPFREE', 'DPGUEST', 'DPVIP', 'DPPASS',

        # Pretix
        'PRETIX', 'PRETIXFREE', 'PRETIXGUEST', 'PRETIXVIP',

        # Stage names
        'STAGE1', 'STAGE2', 'SYSTEMS', 'BIOS', 'EXILE', 'BTC', 'CAFE',
        'WORKSHOP', 'BITCOINTRACK', 'BIOSTRACK', 'SYSTEMSTRACK',

        # Dates
        'OCT3', 'OCT4', 'OCT5', 'OCTOBER3', 'OCTOBER4', 'OCTOBER5',
        'OCT32025', 'OCT42025', 'OCT52025',

        # Related events
        '39C3', 'CCC', '38C3', '40C3',

        # Generic venue
        'CULTUREFREE', 'CULTUREPASS', 'DARKFREE', 'DARKPASS'
    ]


def get_theme_patterns():
    """Thematic keywords from event description"""
    return [
        'CRYPTOANARCHY', 'ANARCHO', 'ANARCHY',
        'PRIVACY', 'PRIVATE', 'ANONYMOUS', 'ANONYMITY',
        'DECENTRALIZATION', 'DECENTRALIZED', 'DECENTRAL',
        'WEB3', 'BLOCKCHAIN', 'CRYPTO',
        'SOVEREIGNTY', 'SOVEREIGN', 'SELFSO VEREIGN',
        'FREEDOM', 'LIBERTY', 'LIBRE',
        'RESISTANCE', 'DISSENT', 'DISOBEY',
        'TECHNOLOGY', 'BIOLOGY', 'NETWORKS',
        'BATTLEFIELD', 'FRONTIER', 'LIFEBLOOD'
    ]


def get_ctf_patterns():
    """Classic CTF flag formats and encodings"""
    patterns = []

    # CTF flags
    flag_bases = ['FLAG', 'HCCP', 'DARK', 'PRAGUE', 'DP', 'CTF']
    for base in flag_bases:
        patterns.extend([
            f'{base}{{FLAG}}',
            f'{base}{{FREE}}',
            f'{base}{{TICKET}}',
            f'{base}{{VOUCHER}}',
            f'{base}{{2025}}',
            f'{base}{{CTF}}'
        ])

    # Base64 encoded common words
    common_words = ['FLAG', 'FREE', 'TICKET', 'VOUCHER', 'HCCP', 'DARK', 'PRAGUE']
    for word in common_words:
        encoded = base64.b64encode(word.encode()).decode().rstrip('=')
        patterns.append(encoded)

    # Hex encoded
    for word in common_words:
        hex_encoded = word.encode().hex().upper()
        patterns.append(hex_encoded)

    # ROT13
    def rot13(text):
        result = []
        for char in text:
            if 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)

    for word in ['IMDARK', 'VOUCHER', 'TICKET', 'FREE', 'HCCP', 'LUNARPUNK', 'CYPHERPUNK']:
        patterns.append(rot13(word))

    # Leetspeak
    leet_words = [
        'H4CK3R', 'H4X0R', '1337', 'L33T', 'L337', '31337',
        'PWN3D', 'PWND', 'R00T', 'R00T3D', 'N00B', 'PR0',
        'W1N', 'FR33', 'T1CK3T', 'P4SS', 'C0D3', 'FL4G',
        'V0UCH3R', 'VOUCH3R', 'T1CKET', 'TICK3T', 'FRE3',
        'D4RK', 'PR4GUE', 'H@CK', 'CYB3R', 'LUN4R'
    ]
    patterns.extend(leet_words)

    return patterns


def get_imdark_variations():
    """Variations based on IMDARK pattern (pronoun + state)"""
    pronouns = ['IM', 'YOUR', 'WERE', 'THEYRE', 'SHES', 'HES', 'YOU', 'WE', 'THEY', 'IT']
    states = [
        'DARK', 'LIGHT', 'GRAY', 'GREY', 'BLACK', 'WHITE',
        'HAPPY', 'SAD', 'ANGRY', 'EXCITED', 'TIRED',
        'HUNGRY', 'THIRSTY', 'COLD', 'HOT', 'LOST',
        'FREE', 'OPEN', 'CLOSED', 'SECRET', 'HIDDEN'
    ]

    patterns = []
    for pronoun in pronouns:
        for state in states:
            patterns.append(f"{pronoun}{state}")
            patterns.append(f"{pronoun}ARE{state}")
            patterns.append(f"{pronoun}AM{state}")
            patterns.append(f"{pronoun}IS{state}")

    return patterns


def get_common_discount_patterns():
    """Generic discount/promo patterns"""
    return [
        'GUEST', 'GUESTPASS', 'GUEST2025', 'GUEST2024', 'NEWGUEST',
        'VISITOR', 'ATTENDEE', 'PARTICIPANT',
        'FREE', 'FREEPASS', 'FREE2025', 'FREETIX', 'FREETICKET',
        'VIP', 'VIPPASS', 'VIP2025',
        'SAVE10', 'SAVE20', 'SAVE30', 'SAVE40', 'SAVE50',
        'OFF10', 'OFF20', 'OFF30', 'OFF40', 'OFF50',
        'DISCOUNT', 'DISCOUNT10', 'DISCOUNT20', 'DISCOUNT30',
        'PROMO', 'PROMO2025', 'PROMO2024', 'SPECIAL', 'SPECIAL2025',
        'EARLYBIRD', 'LATEBIRD', 'LASTMINUTE', 'FLASH',
        'LIMITED', 'EXCLUSIVE', 'MEMBER', 'INSIDER',
        'SPEAKER', 'SPEAKERPASS', 'SPEAKER2025',
        'ORGANIZER', 'ORGPASS', 'ORG2025',
        'VOLUNTEER', 'STAFF', 'STAFFPASS', 'CREW', 'CREWPASS',
        'SPONSOR', 'PARTNER', 'MEDIA', 'PRESS',
        'ADMIN', 'PASSWORD', 'SECRET', 'HIDDEN', 'BACKDOOR',
        'TEST', 'DEMO', 'TRIAL', 'BETA', 'ALPHA'
    ]


def get_priority_codes():
    """Highest probability codes to test first"""
    return [
        # KATKA (worked last year!)
        'KATKAGUEST', 'KATKA', 'KATKA2025', 'KK', 'KKGUEST',

        # Punk movements (event theme)
        'LUNARPUNK', 'LUNARPUNK25', 'LUNARPUNKFREE', 'LUNARPUNKGUEST',
        'CYPHERPUNK', 'CYPHERPUNK25', 'CYPHERPUNKFREE', 'CYPHERPUNKGUEST',

        # Key projects/talks
        'DARKFI', 'DARKFIGUEST', 'NETWORKSTATES', 'NYMVPN',

        # Main speakers + GUEST
        'GAVINGUEST', 'GAVINWOOD', 'CODYWILSON', 'AMIRGUEST', 'AMIRTAAKI',
        'HARRYGUEST', 'HARRYHALPIN', 'JARRADGUEST', 'JARRADHOPE',

        # Venue
        'SECONDCULTURE', 'DP25', 'DARKPRAGUE2025', 'SCGUEST', 'DPGUEST',

        # Generic high-prob
        'GUEST2025', 'FREE2025', 'HCCP2025', 'CTF2025',

        # Control (for validation)
        'IMDARK'
    ]


def get_master_wordlist():
    """Get all voucher patterns combined"""
    all_patterns = []

    all_patterns.extend(get_katka_patterns())
    all_patterns.extend(get_punk_movement_patterns())
    all_patterns.extend(get_talk_event_patterns())
    all_patterns.extend(get_speaker_patterns())
    all_patterns.extend(get_sponsor_patterns())
    all_patterns.extend(get_venue_event_patterns())
    all_patterns.extend(get_theme_patterns())
    all_patterns.extend(get_ctf_patterns())
    all_patterns.extend(get_imdark_variations())
    all_patterns.extend(get_common_discount_patterns())

    # Remove duplicates and sort
    return sorted(list(set(all_patterns)))


def load_custom_wordlist(filepath):
    """Load additional codes from text file"""
    if not os.path.exists(filepath):
        return []

    codes = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                codes.append(line.upper())

    return codes


def get_wordlist_stats():
    """Get statistics about the wordlist"""
    master = get_master_wordlist()
    priority = get_priority_codes()

    return {
        'total_patterns': len(master),
        'priority_patterns': len(priority),
        'categories': {
            'katka': len(get_katka_patterns()),
            'punk_movements': len(get_punk_movement_patterns()),
            'talks': len(get_talk_event_patterns()),
            'speakers': len(get_speaker_patterns()),
            'sponsors': len(get_sponsor_patterns()),
            'venue': len(get_venue_event_patterns()),
            'themes': len(get_theme_patterns()),
            'ctf': len(get_ctf_patterns()),
            'imdark': len(get_imdark_variations()),
            'common': len(get_common_discount_patterns())
        }
    }


if __name__ == "__main__":
    # Show stats when run directly
    stats = get_wordlist_stats()
    print("=" * 60)
    print("MASTER WORDLIST STATISTICS")
    print("=" * 60)
    print(f"\nTotal unique patterns: {stats['total_patterns']}")
    print(f"Priority patterns: {stats['priority_patterns']}")
    print("\nBreakdown by category:")
    for category, count in sorted(stats['categories'].items()):
        print(f"  {category:20s}: {count:4d} patterns")

    print("\n" + "=" * 60)
    print("PRIORITY CODES (test these first):")
    print("=" * 60)
    for i, code in enumerate(get_priority_codes(), 1):
        print(f"  {i:2d}. {code}")
