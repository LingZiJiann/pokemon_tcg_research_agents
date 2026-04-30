import re


def extract_card_name(raw_input: str) -> dict:
    """Extract card name and condition from raw user input.

    Parses a string containing a card name and optional condition information,
    normalizing the card name and extracting the grading or condition status.

    Args:
        raw_input: String containing the card name and optional condition
            (e.g., "Charizard PSA 10", "Blastoise NM-MT", "Venusaur").

    Returns:
        A dictionary with the following keys:
            name (str): Normalized card name with title case and stripped whitespace.
            condition (str): Card condition, either a grading (e.g., "PSA 10", "BGS 9.5")
                or an ungraded condition (e.g., "NM", "LP", "HP", "DMG"). Defaults to "Raw".
    """
    # Detect condition patterns
    condition = "Raw"

    # Graded conditions: PSA 10, BGS 9.5, CGC 8, etc.
    graded_match = re.search(
        r"\b(PSA|BGS|CGC)\s*(\d+(?:\.\d+)?)\b", raw_input, re.IGNORECASE
    )
    if graded_match:
        condition = f"{graded_match.group(1).upper()} {graded_match.group(2)}"

    # Ungraded condition keywords
    ungraded_keywords = {
        r"\bNM-MT\b": "NM-MT",
        r"\bNear Mint\b": "NM",
        r"\bLightly Played\b": "LP",
        r"\bMP\b": "MP",
        r"\bHP\b": "HP",
        r"\bDMG\b": "DMG",
        r"\bNM\b": "NM",
        r"\bLP\b": "LP",
    }

    if not graded_match:
        for pattern, label in ungraded_keywords.items():
            if re.search(pattern, raw_input, re.IGNORECASE):
                condition = label
                break

    # Strip condition from input to get the card name
    name = raw_input
    name = re.sub(r"\b(PSA|BGS|CGC)\s*\d+(?:\.\d+)?\b", "", name, flags=re.IGNORECASE)
    for pattern in ungraded_keywords.keys():
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)

    # Normalize: strip, title case, clean whitespace
    name = name.strip()
    name = " ".join(name.split())  # Collapse multiple spaces
    name = name.title()

    return {"name": name, "condition": condition}
