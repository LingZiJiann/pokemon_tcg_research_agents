# eBay Search Feature

## Overview

The eBay search feature queries recent sold auction listings on eBay via the SerpAPI eBay engine. It accepts structured card data (name + condition) from the card extractor and returns a list of parsed listings with price, URL, and sold date.

## Implementation

### Core Class: `EbaySearch`

**Location:** `src/tools/ebay_search.py`

```python
class EbaySearch:
    def search(self, card_data: dict) -> pd.DataFrame: ...
    def _parse_listing(self, result: dict) -> dict: ...
    def _filter_and_rank(self, results: list[dict], condition: str, search_term: str) -> list[dict]: ...
    def _title_contains_condition(self, title: str, condition: str) -> bool: ...
```

### `search()`

```python
def search(self, card_data: dict) -> pd.DataFrame:
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
A pandas DataFrame with columns:
| Column | Type | Description |
|--------|------|-------------|
| `url` | str | eBay listing URL |
| `title` | str | Listing title as shown on eBay |
| `price` | float | Extracted sale price (USD) |
| `sold_date` | str | Date the listing sold |
| `score` | int | Relevance score vs search term (0–100) |

Results are sorted by `score` descending — most relevant titles first.

### `_parse_listing()`

Internal helper that extracts `url`, `title`, `price`, and `sold_date` from a raw SerpAPI organic result dict.

### `_filter_and_rank()`

Filters parsed results to those whose title contains the condition string, scores each against the search term using `rapidfuzz.fuzz.token_set_ratio`, and returns only results with a score greater than or equal to the configured `MIN_SCORE`. Results are sorted by score descending.

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

## Configuration

Configuration settings for the eBay search tool are stored in `config/ebay_search_config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MIN_SCORE` | `100` | Minimum fuzzy match score (0–100) required for results to be included. Only results with a score ≥ `MIN_SCORE` are returned. |

To adjust the minimum score threshold, modify the `MIN_SCORE` value in `config/ebay_search_config.py`.

## Usage Examples

### Example 1: Graded Card Search

```python
ebay = EbaySearch()
results = ebay.search({"name": "Charizard 199/165 Obsidian Flames", "condition": "PSA 10"})
# Searches eBay for: "Charizard 199/165 Obsidian Flames PSA 10"
```

**Sample output (DataFrame):**
```
                              url                                              title  price      sold_date  score
0  https://www.ebay.com/itm/...  Charizard 199/165 Obsidian Flames PSA 10 Poke...  320.00  Apr 28, 2026     92
1  https://www.ebay.com/itm/...  Charizard 199/165 Obsidian Flames PSA 10 Raw ...  245.50  Apr 27, 2026     88
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
results_df = ebay_search.search(extraction)  # extraction = output of extract_card_name()

# Access as DataFrame
print(results_df[["url", "price", "sold_date"]])

# Iterate through rows
for _, row in results_df.iterrows():
    print(row["url"])
    print(row["price"])
    print(row["sold_date"])
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

After parsing, `_filter_and_rank` handles four steps in one pass:
1. Filters to results whose title contains the condition string (case-insensitive) via `_title_contains_condition`
2. Scores each title against the search term using `rapidfuzz.fuzz.token_set_ratio` (0–100)
3. Only includes results where `score >= MIN_SCORE` (configured in `config/ebay_search_config.py`)
4. Returns results sorted by score descending so the most relevant listings appear first

`token_set_ratio` is used because eBay titles contain extra words (set numbers, grades, seller tags) that would penalise simpler scorers. The `MIN_SCORE` threshold ensures only sufficiently relevant matches are returned.

### Error Handling

Any exception from the SerpAPI client is logged at `ERROR` level and re-raised to the caller.

## Future Enhancements

- Filter results by date range (e.g., last 30 days only)
- Support `Buy It Now` format in addition to auctions
- Return raw price range statistics (min, max, median, average)
- Cache recent searches to avoid redundant API calls
- Support pagination for larger result sets
