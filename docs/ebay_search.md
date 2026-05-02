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
    def _filter_and_rank(self, results: list[dict], condition: str, search_term: str) -> list[dict]: ...
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
        "sold_date": str,   # Date the listing sold
        "score": int        # Relevance score vs search term (0–100)
    },
    ...
]
```

Results are sorted by `score` descending — most relevant titles first.

### `_parse_listing()`

Internal helper that extracts `url`, `title`, `price`, and `sold_date` from a raw SerpAPI organic result dict.

### `_filter_and_rank()`

Filters parsed results to those whose title contains the condition string, scores each against the search term using `rapidfuzz.fuzz.token_set_ratio`, and returns them sorted by score descending.

### `_title_contains_condition()`

Checks whether a listing title contains the card condition string (case-insensitive substring match). For example, a title must contain `"NM"` when searching for near-mint cards.

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
        "title": "Charizard 199/165 Obsidian Flames PSA 10 Pokemon Card",
        "price": 320.00,
        "sold_date": "Apr 28, 2026",
        "score": 92
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

### Result Filtering and Ranking

After parsing, `_filter_and_rank` handles three steps in one pass:
1. Filters to results whose title contains the condition string (case-insensitive) via `_title_contains_condition`
2. Scores each title against the search term using `rapidfuzz.fuzz.token_set_ratio` (0–100)
3. Sorts results by score descending so the most relevant listings appear first

`token_set_ratio` is used because eBay titles contain extra words (set numbers, grades, seller tags) that would penalise simpler scorers.

### Error Handling

Any exception from the SerpAPI client is logged at `ERROR` level and re-raised to the caller.

## Future Enhancements

- Filter results by date range (e.g., last 30 days only)
- Support `Buy It Now` format in addition to auctions
- Return raw price range statistics (min, max, median, average)
- Cache recent searches to avoid redundant API calls
- Support pagination for larger result sets
