import re

# Pattern to detect graded cards (PSA, BGS, CGC with numeric grade)
GRADED_PATTERN = re.compile(r"\b(PSA|BGS|CGC)\s*(\d+(?:\.\d+)?)\b", re.IGNORECASE)

# Patterns to detect ungraded card conditions
UNGRADED_CONDITIONS = [
    (re.compile(r"\bNM-MT\b", re.IGNORECASE), "nm-mt"),
    (re.compile(r"\bNear Mint\b", re.IGNORECASE), "nm"),
    (re.compile(r"\bLightly Played\b", re.IGNORECASE), "lp"),
    (re.compile(r"\bMP\b", re.IGNORECASE), "mp"),
    (re.compile(r"\bHP\b", re.IGNORECASE), "hp"),
    (re.compile(r"\bDMG\b", re.IGNORECASE), "dmg"),
    (re.compile(r"\bNM\b", re.IGNORECASE), "nm"),
    (re.compile(r"\bLP\b", re.IGNORECASE), "lp"),
]

# Pattern to clean up condition markers from card names
CLEANUP_PATTERN = re.compile(
    r"\b(PSA|BGS|CGC)\s*\d+(?:\.\d+)?\b|\bNM-MT\b|\bNear Mint\b|\bLightly Played\b|\bMP\b|\bHP\b|\bDMG\b|\bNM\b|\bLP\b",
    re.IGNORECASE,
)
