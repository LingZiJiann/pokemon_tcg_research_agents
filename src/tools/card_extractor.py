import re

from src.utils.logger import get_logger

logger = get_logger("card_extraction")

_GRADED_PATTERN = re.compile(r"\b(PSA|BGS|CGC)\s*(\d+(?:\.\d+)?)\b", re.IGNORECASE)

_UNGRADED_CONDITIONS = [
    (re.compile(r"\bNM-MT\b", re.IGNORECASE), "nm-mt"),
    (re.compile(r"\bNear Mint\b", re.IGNORECASE), "nm"),
    (re.compile(r"\bLightly Played\b", re.IGNORECASE), "lp"),
    (re.compile(r"\bMP\b", re.IGNORECASE), "mp"),
    (re.compile(r"\bHP\b", re.IGNORECASE), "hp"),
    (re.compile(r"\bDMG\b", re.IGNORECASE), "dmg"),
    (re.compile(r"\bNM\b", re.IGNORECASE), "nm"),
    (re.compile(r"\bLP\b", re.IGNORECASE), "lp"),
]

_CLEANUP_PATTERN = re.compile(
    r"\b(PSA|BGS|CGC)\s*\d+(?:\.\d+)?\b|\bNM-MT\b|\bNear Mint\b|\bLightly Played\b|\bMP\b|\bHP\b|\bDMG\b|\bNM\b|\bLP\b",
    re.IGNORECASE,
)


def extract_card_name(raw_input: str) -> dict:
    """Extract card name and condition from raw user input.

    Returns a dict with "name" (normalized) and "condition" (graded or ungraded,
    defaults to "Raw" if not detected).

    Examples:
        "Charizard PSA 10" → {"name": "charizard", "condition": "psa 10"}
        "Blastoise NM-MT" → {"name": "blastoise", "condition": "nm-mt"}
        "Venusaur" → {"name": "venusaur", "condition": "raw"}
    """
    condition = "raw"

    # Check for graded condition (PSA, BGS, CGC with numeric grade)
    graded_match = _GRADED_PATTERN.search(raw_input)
    if graded_match:
        condition = f"{graded_match.group(1).lower()} {graded_match.group(2)}"
        logger.debug(f"Detected graded condition: {condition}")
    else:
        # Check for ungraded conditions only if no grading found
        for pattern, label in _UNGRADED_CONDITIONS:
            if pattern.search(raw_input):
                condition = label
                logger.debug(f"Detected ungraded condition: {condition}")
                break

    # Remove condition markers and normalize whitespace/case
    name = _CLEANUP_PATTERN.sub("", raw_input).strip()
    name = " ".join(name.split())
    name = name.lower()

    result = {"name": name, "condition": condition}
    logger.debug(f"Extracted card: {result}")
    return result
