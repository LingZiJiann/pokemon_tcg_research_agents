from config.card_extraction_config import (
    CLEANUP_PATTERN,
    GRADED_PATTERN,
    UNGRADED_CONDITIONS,
)
from src.utils.logger import get_logger

logger = get_logger("card_extraction")


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
    graded_match = GRADED_PATTERN.search(raw_input)
    if graded_match:
        condition = f"{graded_match.group(1).lower()} {graded_match.group(2)}"
        logger.debug(f"Detected graded condition: {condition}")
    else:
        # Check for ungraded conditions only if no grading found
        for pattern, label in UNGRADED_CONDITIONS:
            if pattern.search(raw_input):
                condition = label
                logger.debug(f"Detected ungraded condition: {condition}")
                break

    # Remove condition markers and normalize whitespace/case
    name = CLEANUP_PATTERN.sub("", raw_input).strip()
    name = " ".join(name.split())
    name = name.lower()

    result = {"name": name, "condition": condition}
    logger.debug(f"Extracted card: {result}")
    return result
