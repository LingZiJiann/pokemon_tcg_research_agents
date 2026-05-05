# Card Extraction Feature

## Overview

The card extraction feature normalizes raw user input into structured data by parsing the **card name** and **condition** separately. This enables more accurate searching and data organization for Pokemon card research.

## Implementation

### Core Function: `extract_card_name()`

**Location:** `src/tools/card_extractor.py`

```python
def extract_card_name(raw_input: str) -> dict:
    """Extract card name and condition from raw user input."""
```

**Return Type:**
```python
{
    "name": str,        # Normalized card name (e.g., "charizard 199/165 obsidian flames")
    "condition": str    # Card condition (e.g., "psa 10", "nm", "raw")
}
```

## Supported Conditions

### Graded Conditions
- **psa**: `psa 10`, `psa 9`, `psa 8.5`, etc.
- **bgs**: `bgs 9.5`, `bgs 9`, etc.
- **cgc**: `cgc 10`, `cgc 8`, etc.

Format: `{grade} {score}` (lowercase)

### Ungraded Conditions
- `nm-mt` (Near Mint-Mint)
- `nm` (Near Mint)
- `lp` (Lightly Played)
- `mp` (Moderately Played)
- `hp` (Heavily Played)
- `dmg` (Damaged)

### Default
If no condition is detected, defaults to `"raw"` (ungraded).

## Usage Examples

### Example 1: Graded Card
```
Input:  "psa 10 charizard 199/165 obsidian flames"
Output: {
    "name": "charizard 199/165 obsidian flames",
    "condition": "psa 10"
}
```

### Example 2: Ungraded Card
```
Input:  "NM blastoise base set"
Output: {
    "name": "blastoise base set",
    "condition": "nm"
}
```

### Example 3: No Condition Specified
```
Input:  "charizard unlimited"
Output: {
    "name": "charizard unlimited",
    "condition": "raw"
}
```

## Integration with Main Flow

The extraction is integrated into the main CLI flow in `main.py`:

```python
from src.tools.card_extractor import extract_card_name

extraction = extract_card_name(user_input)
print(f"Extracted Name: {extraction['name']}")
print(f"Condition: {extraction['condition']}")
```

## Implementation Details

### Extraction Logic

1. **Condition Detection** (regex-based):
   - Scans input for graded patterns: `(PSA|BGS|CGC) \d+(\.\d+)?`
   - Scans for ungraded keywords: `NM`, `LP`, `MP`, etc.
   - Defaults to `"Raw"` if nothing matches

2. **Name Normalization**:
   - Removes detected condition tokens from input
   - Strips whitespace and collapses multiple spaces
   - Converts to lowercase for consistency (e.g., "Charizard" → "charizard")

### Edge Cases Handled

- Mixed case input (e.g., "PSA 10" or "psa 10")
- Extra whitespace (e.g., "psa  10  charizard")
- Condition at any position in input
- Multiple spaces between tokens

## Future Enhancements

- Persist cache to a JSON/SQLite database for cross-session lookups
- Add support for additional grading companies (Sportscard Guaranty, etc.)
- Extract set information and card number separately
- Validate extracted card names against a Pokemon card database
