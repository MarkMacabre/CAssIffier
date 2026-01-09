"""Category definitions for audio sample classification."""

# Main categories and their subcategories
CATEGORIES = {
    "Drums": {
        "subcategories": ["Kicks", "Snares", "Claps", "HiHats", "Cymbals", "Percussion"],
        "genre_aware": True
    },
    "Bass": {
        "subcategories": ["Synth", "Acoustic", "808"],
        "genre_aware": True
    },
    "Synths": {
        "subcategories": ["Leads", "Pads", "Plucks", "Arps"],
        "genre_aware": False
    },
    "Instruments": {
        "subcategories": ["Piano", "Guitar", "Strings", "Brass"],
        "genre_aware": False
    },
    "FX": {
        "subcategories": [],
        "genre_aware": False
    },
    "Vocals": {
        "subcategories": [],
        "genre_aware": False
    },
    "Unknown": {
        "subcategories": [],
        "genre_aware": False
    }
}

# Common genres for genre-aware categories
GENRES = [
    "Techno", "House", "Dubstep", "Trap", "Hip-Hop", "DnB", "Ambient",
    "Industrial", "EDM", "Trance", "Electro"
]

# Keywords for rule-based classification
CATEGORY_KEYWORDS = {
    "Drums": {
        "Kicks": ["kick", "bd", "bassdrum"],
        "Snares": ["snare", "sn", "sd"],
        "Claps": ["clap", "handclap", "cp"],
        "HiHats": ["hihat", "hh", "hat", "closedhat", "openhat", "chh", "ohh"],
        "Cymbals": ["cymbal", "crash", "ride"],
        "Percussion": ["perc", "percussion", "conga", "bongo", "tom", "shaker", "tambourine"]
    },
    "Bass": {
        "Synth": ["bass", "subbass", "sub"],
        "Acoustic": ["acousticbass", "upright", "contrabass"],
        "808": ["808", "tr808"]
    },
    "Synths": {
        "Leads": ["lead", "melody", "synth"],
        "Pads": ["pad", "atmosphere", "atmos"],
        "Plucks": ["pluck", "stab"],
        "Arps": ["arp", "arpeggio"]
    },
    "Instruments": {
        "Piano": ["piano", "key", "keys"],
        "Guitar": ["guitar", "gtr"],
        "Strings": ["string", "violin", "cello", "orchestra"],
        "Brass": ["brass", "trumpet", "horn", "trombone"]
    },
    "FX": ["fx", "effect", "riser", "sweep", "impact", "whoosh", "transition"],
    "Vocals": ["vocal", "vox", "voice", "acapella", "spoken"]
}

# Genre keywords for detection
GENRE_KEYWORDS = {
    "Techno": ["techno"],
    "House": ["house", "deephouse", "techhouse"],
    "Dubstep": ["dubstep", "dub"],
    "Trap": ["trap"],
    "Hip-Hop": ["hiphop", "hip-hop", "rap"],
    "DnB": ["dnb", "drumandbass", "drumnbass", "jungle"],
    "Ambient": ["ambient", "drone"],
    "Industrial": ["industrial", "hard"],
    "EDM": ["edm"],
    "Trance": ["trance", "psy"],
    "Electro": ["electro"]
}


def get_all_categories():
    """Get list of all main categories."""
    return list(CATEGORIES.keys())


def get_subcategories(category):
    """Get subcategories for a given category."""
    return CATEGORIES.get(category, {}).get("subcategories", [])


def is_genre_aware(category):
    """Check if a category should be genre-aware."""
    return CATEGORIES.get(category, {}).get("genre_aware", False)
