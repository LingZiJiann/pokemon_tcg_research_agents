# EDA Agent

## Overview

The EDA agent interprets a pandas DataFrame of eBay sold listings for a Pokemon card and returns a plain-language pricing analysis via a single Claude call. It computes summary statistics and detects outliers in Python, then hands the structured result to Claude for a concise buyer-facing interpretation.

## Implementation

### Core Class: `EdaAgent`

**Location:** `src/agents/eda_agent.py`

```python
class EdaAgent:
    async def run(self, ebay_df: pd.DataFrame) -> str: ...
    def _compute_stats(self, df: pd.DataFrame) -> dict: ...
    def _build_prompt(self, stats: dict, df: pd.DataFrame) -> str: ...
```

### `run()`

```python
async def run(self, ebay_df: pd.DataFrame) -> str:
    """Compute pricing stats and return Claude's interpretation."""
```

**Input:** A pandas DataFrame produced by `EbaySearch.search()` with at least `price` (float) and `sold_date` (str) columns.

**Output:** A plain-text string — Claude's concise interpretation of the pricing data.

**Flow:**

```
ebay_df
  └─ _compute_stats()   ← pure Python, no Claude
       └─ _build_prompt()
            └─ Claude call (claude-haiku-4-5, single message)
                 └─ returns interpretation string
```

### `_compute_stats()`

Computes the following from the `price` column (after dropping nulls):

| Stat | Description |
|------|-------------|
| `count` | Number of valid price entries |
| `mean` | Average sale price |
| `median` | Median sale price |
| `std` | Standard deviation |
| `min` / `max` | Cheapest and most expensive sale |
| `outlier_count` | Number of prices outside `Q1 − 1.5×IQR` or `Q3 + 1.5×IQR` |
| `outlier_values` | The actual outlier prices |
| `date_range` | Earliest to latest `sold_date` in the dataset |

### `_build_prompt()`

Formats the computed stats and the full raw price list into a structured text block that is sent as the user message to Claude. The system prompt is:

> "You are a data analyst specialising in Pokemon card pricing."

The user message asks Claude to produce a concise plain-language interpretation, highlighting trends, outliers, and buyer-relevant signals.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `anthropic_api_key` | `""` | Read from `ANTHROPIC_API_KEY` in `.env` |
| `anthropic_model` | `"claude-haiku-4-5-20251001"` | Model used for the Claude call |

Both are managed by the unified pydantic `Settings` class in `config/config.py`.

## Usage Example

```python
import asyncio
import pandas as pd
from src.agents.eda_agent import EdaAgent

df = pd.DataFrame([
    {"price": 320.0, "sold_date": "Apr 28, 2026"},
    {"price": 245.5, "sold_date": "Apr 27, 2026"},
    {"price": 310.0, "sold_date": "Apr 25, 2026"},
])

summary = asyncio.run(EdaAgent().run(df))
print(summary)
```

**Sample output:**
```
The 3 listings show a tight price band between $245.50 and $320.00, with a median of
$310.00 and low standard deviation ($38.96), suggesting stable demand. No IQR outliers
were detected. All sales occurred within the last week, indicating recent market activity.
The $245.50 sale is notably lower — worth checking whether it was a raw vs. graded copy.
```

## Integration with Orchestrator

`EdaAgent.run()` is called inside `Orchestrator.run()` after `EbaySearch.search()` returns:

```python
# src/orchestrator.py
eda_summary = await EdaAgent().run(ebay_df)
print(eda_summary)
```

In Phase 2 and beyond it runs concurrently with the research pipeline:

```python
eda_summary, overview = await asyncio.gather(
    EdaAgent().run(ebay_df),
    self._research_pipeline(card_data),
)
```

## Design Notes

- **No tools, no streaming** — a single `messages.create` call is sufficient; the dataset is small enough to fit in one prompt.
- **Stats computed in Python, not by Claude** — keeps the Claude call deterministic and cheaper. Claude only provides the natural-language layer on top of numbers it did not compute.
- **`AsyncAnthropic` client** — matches the async orchestrator so the call can be awaited without blocking the event loop.

## Future Enhancements

- Add a `condition_breakdown` stat (count and mean price per condition label) for mixed DataFrames
- Detect price trend direction (rising / falling) by correlating price against `sold_date`
- Return a structured `EDAResult` dataclass in addition to the Claude summary so downstream agents can access raw stats without re-parsing text
