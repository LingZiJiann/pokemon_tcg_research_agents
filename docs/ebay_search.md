# eBay Search Feature

## Overview

The eBay search feature queries recent sold auction listings on eBay via the SerpAPI eBay engine. It accepts structured card data (name + condition) from the card extractor and returns a list of parsed listings with price, URL, and sold date.

## Implementation

### Core Class: `EbaySearch`

**Location:** `src/tools/ebay_search.py`

```python
class EbaySearch:
    def search(self, card_data: dict) -> list[dict]: ...
    def _parse_listing(self, result: dict) -> dict: ...
    def _title_matches_card_name(self, title: str, card_name: str) -> bool: ...
    def _title_contains_condition(self, title: str, condition: str) -> bool: ...
```

### `search()`

```python
def search(self, card_data: dict) -> list[dict]:
    """Search eBay for a card based on card extractor results."""
```

**Input:**
```python
{
    "name": str,       # Normalized card name (e.g., "Charizard 199/165 Obsidian Flames")
    "condition": str   # Card condition (e.g., "PSA 10", "NM", "Raw")
}
```

**Output:**
```python
[
    {
        "url": str,         # eBay listing URL
        "title": str,       # Listing title as shown on eBay
        "price": float,     # Extracted sale price (USD)
        "sold_date": str    # Date the listing sold
    },
    ...
]
```

### `_parse_listing()`

Internal helper that extracts `url`, `title`, `price`, and `sold_date` from a raw SerpAPI organic result dict.

### `_title_contains_condition()`

Checks whether a listing title contains the card condition string (case-insensitive substring match). For example, a title must contain `"NM"` when searching for near-mint cards.

### `_title_matches_card_name()`

Fuzzy-matches the card name against the listing title using `difflib.SequenceMatcher`. The similarity ratio must meet `fuzzy_threshold` (default `0.4`) for the listing to pass. This filters out listings that returned via keyword search but don't actually match the card.

Both `_title_contains_condition` and `_title_matches_card_name` must return `True` for a result to be included.

## Search Parameters

The following SerpAPI parameters are fixed per search:

| Parameter       | Value    | Description                          |
|-----------------|----------|--------------------------------------|
| `engine`        | `"ebay"` | Routes the query to eBay             |
| `show_only`     | `"Sold"` | Filters to sold listings only        |
| `buying_format` | `"Auction"` | Filters to auction-style sales    |
| `_nkw`          | dynamic  | Keyword query: `"{name} {condition}"` |

## Usage Examples

### Example 1: Graded Card Search

```python
ebay = EbaySearch()
results = ebay.search({"name": "Charizard 199/165 Obsidian Flames", "condition": "PSA 10"})
# Searches eBay for: "Charizard 199/165 Obsidian Flames PSA 10"
```

**Sample output:**
```python
[
    {
        "url": "https://www.ebay.com/itm/...",
        "price": 320.00,
        "sold_date": "Apr 28, 2026"
    },
    ...
]
```

### Example 2: Ungraded Card Search

```python
results = ebay.search({"name": "Blastoise Base Set", "condition": "NM"})
# Searches eBay for: "Blastoise Base Set NM"
```

## Integration with Main Flow

The search is integrated into the main CLI flow in `main.py`:

```python
from src.tools.ebay_search import EbaySearch

ebay_search = EbaySearch()
results = ebay_search.search(extraction)  # extraction = output of extract_card_name()

for result in results:
    print(result["url"])
    print(result["price"])
    print(result["sold_date"])
```

The `extraction` dict from `extract_card_name()` is passed directly to `EbaySearch.search()` — no transformation needed.

## Implementation Details

### Query Construction

The search term is built by concatenating name and condition:

```python
search_term = f"{card_data['name']} {card_data['condition']}"
```

For example, `"Charizard 199/165 Obsidian Flames"` + `"PSA 10"` → `"Charizard 199/165 Obsidian Flames PSA 10"`.

### SerpAPI Client

Instantiated per search call using the `serpapi` package:

```python
client = serpapi.Client(api_key=self.api_key)
results = client.search(params)
```

The API key is read from the `SERPAPI_API_KEY` environment variable if not passed directly to the constructor.

### Result Parsing

Only `organic_results` are used from the SerpAPI response. Each result is parsed to extract:
- `link` → `url`
- `price.extracted` → `price` (numeric float)
- `sold_date` → `sold_date`

Fields missing from a result default to `None`.

### Result Filtering

After parsing, results are filtered by two checks applied in sequence:

1. **Condition match** — `_title_contains_condition`: the title must contain the condition string (e.g. `"NM"`) as a case-insensitive substring.
2. **Card name fuzzy match** — `_title_matches_card_name`: `difflib.SequenceMatcher` computes a similarity ratio between the card name and the title. Only results at or above `fuzzy_threshold` (default `0.4`) are kept.

The threshold can be tuned at construction time:
```python
ebay = EbaySearch(fuzzy_threshold=0.6)  # stricter
ebay = EbaySearch(fuzzy_threshold=0.3)  # more lenient
```

### Error Handling

Any exception from the SerpAPI client is logged at `ERROR` level and re-raised to the caller.

## Future Enhancements

- Filter results by date range (e.g., last 30 days only)
- Support `Buy It Now` format in addition to auctions
- Return raw price range statistics (min, max, median, average)
- Cache recent searches to avoid redundant API calls
- Support pagination for larger result sets
