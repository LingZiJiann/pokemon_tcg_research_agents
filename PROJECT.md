# Pokemon Card Research Agents

A CLI multi-agent pipeline that takes a Pokemon card query, fetches recent eBay sold prices, and produces an AI-powered pricing analysis — built on Claude (Anthropic SDK) with an async pipeline.

## Overview

```
uv run main.py
→ "What card are you searching for?"
→ User types: "charizard psa 10"
→ Pipeline runs:
    1. extract_card_name        → {"name": "charizard", "condition": "psa 10"}
    2. EbaySearch.search()      → DataFrame of recent sold listings
    3. EdaAgent.run()           → Claude pricing interpretation
→ Prints EDA summary
```

## Project Structure

```
main.py                        # CLI entry point — delegates to Pipeline
config/
  config.py                    # Unified pydantic Settings (API keys, model, thresholds, regex)
src/
  pipeline.py                  # Async pipeline coordinator
  agents/
    eda_agent.py               # Computes price stats + calls Claude for interpretation
    research_agent.py          # (legacy) Claude agent with tool use
  tools/
    card_extractor.py          # Normalizes messy card input
    ebay_search.py             # SerpAPI eBay sold listings lookup
    research_tools.py          # Tavily web search tool
  utils/
    logger.py                  # Logging utility
docs/
  card_extraction.md           # Card extraction feature documentation
  ebay_search.md               # eBay search feature documentation
  eda_agent.md                 # EDA agent feature documentation
```

## Tools & Agents

| Component | Type | Description |
|---|---|---|
| `extract_card_name` | Plain Python | Normalizes user input into name + condition dict |
| `EbaySearch.search()` | Plain Python | Queries SerpAPI eBay sold listings; filters by condition and fuzzy score |
| `EdaAgent` | Claude agent | Computes price stats (mean, median, IQR outliers, date range) then calls Claude for a buyer-facing interpretation |

## Setup

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
uv sync
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Optional overrides (pydantic Settings)
MIN_EBAY_SCORE=100             # Minimum fuzzy match score for eBay results (default 100)
```

### Run

```bash
uv run main.py
```

## Dependencies

- `anthropic` — Claude SDK (tool use)
- `serpapi` / `google-search-results` — SerpAPI client
- `tavily-python` — Tavily web search client
- `rapidfuzz` — fuzzy string matching for relevance ranking
- `pydantic-settings` — unified config via `.env` and environment variables
- `pandas` — DataFrame for eBay results

---

## Roadmap

### ~~Phase 1 — EDA Agent~~ ✓ Complete

- `EdaAgent` computes price stats (count, mean, median, std, IQR outliers, date range) and calls Claude for a plain-language interpretation
- `Pipeline` implementation wires: `extract_card_name → EbaySearch.search → EdaAgent.run → print`
- `main.py` delegates entirely to `asyncio.run(Pipeline().run(...))`

---

### Phase 2 — Research Pipeline

Spawn 3 concurrent Tavily search agents and consolidate results into a market overview, then run EDA and research in parallel.

**Target architecture:**

```
User Input
    │
    ▼
extract_card_name → EbaySearch.search
    │
    ├────────────────────────────────────┐
    ▼                                    ▼
EdaAgent.run()                  _research_pipeline()
                                  ├─ SearchAgent (investment)
                                  ├─ SearchAgent (reddit)
                                  └─ SearchAgent (pricecharting)
                                        │
                                  ConsolidationAgent.run()
    │                                    │
    └──────────────┬─────────────────────┘
                   ▼
          AnalystAgent.run()   ← Phase 3
```

**Agents to build:**

| Agent | File | Responsibility |
|---|---|---|
| `SearchAgent` | `src/agents/search_agent.py` | Calls Tavily directly — no Claude, pure tool invocation |
| `ConsolidationAgent` | `src/agents/consolidation_agent.py` | Single Claude call to merge 3 search results into a market overview |

---

### Phase 3 — Analyst Agent & Final Output

Combine EDA and research overview into a final buy/hold/sell recommendation and print all three sections with clear headers.

**Agent to build:**

| Agent | File | Responsibility |
|---|---|---|
| `AnalystAgent` | `src/agents/analyst_agent.py` | Single Claude call — produces buy/hold/sell recommendation from EDA + overview |

**Final output format:**
```
=== EDA Summary ===
...

=== Market Overview ===
...

=== Analyst Recommendation ===
...
```

---

### Phase 4 — Quality & Interface

- Confidence score on analyst output (e.g. "low confidence — only 3 sold listings")
- SQLite cache to avoid redundant SerpAPI/Tavily calls
- Wrap CLI in FastAPI + minimal frontend for non-technical users
- Export recommendations as PDF or CSV