import re

# Expanded banned words list (customize as needed)
BANNED_WORDS = [
    "badword", "fuck", "shit", "bitch", "asshole", "bastard",
    "dick", "pussy", "cunt", "nigger", "nigga", "faggot",
    "retard", "whore", "slut", "damn", "crap",
]

# Build regex pattern – word boundaries, case-insensitive
_pattern = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b",
    re.IGNORECASE,
)


def filter_message(text: str) -> str:
    """Replace banned words with asterisks of the same length."""
    def replace(match):
        return "*" * len(match.group())
    return _pattern.sub(replace, text)
