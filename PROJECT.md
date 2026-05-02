# Pokemon Card Research Agents

A CLI AI agent that takes a Pokemon card query, normalizes it, and returns recent eBay sold prices — powered by Claude (Anthropic SDK) with tool use.

## Overview

```
uv run main.py
→ "What card are you searching for?"
→ User types: "charizard 199/165 obsidian flames"
→ Agent runs two tools in sequence:
    1. extract_card_name        → "Charizard 199/165 Obsidian Flames"
    2. search_ebay_last_sold    → recent sold listings from SerpAPI
→ Agent formats and prints results
```

## Project Structure

```
main.py                        # CLI entry point
src/
  agents/
    research_agent.py          # Claude agent with tool use
  tools/
    card_extractor.py          # Normalizes messy card input
    ebay_search.py             # SerpAPI eBay sold listings lookup
  utils/
    logger.py                  # Logging utility
docs/
  card_extraction.md           # Card extraction feature documentation
  ebay_search.md               # eBay search feature documentation
```

**Future-proofing:** When an orchestrator is needed, it slots in as `src/orchestrator.py` and treats each file in `src/agents/` as a delegatable subagent — no restructuring required.

## Tools

| Tool | Description |
|---|---|
| `extract_card_name` | Normalizes user input into a clean search string (e.g. "Charizard 199/165 Obsidian Flames") |
| `search_ebay_last_sold` | Queries SerpAPI eBay sold listings; filters by condition match, scores titles with `rapidfuzz` for relevance, returns results as a pandas DataFrame sorted by score with columns: url, title, price, sold_date, score |

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
```

### Run

```bash
uv run main.py
```

## Dependencies

- `anthropic` — Claude SDK (tool use)
- `google-search-results` — SerpAPI client
- `rapidfuzz` — fuzzy string matching for relevance ranking
- `python-dotenv` — load `.env`

---

## Roadmap

### Phase 2 — Orchestrated Multi-Agent Pipeline

Expand the current single-agent flow into a parallel multi-agent architecture. Each agent is a specialist; an orchestrator coordinates them and a synthesis agent produces the final output.

**Target architecture:**

```
User Input
    │
    ▼
extract_card_name
    │
    ▼
search_ebay_last_sold
    │
    ├──────────────────────────┐
    ▼                          ▼
[context_agent]          [eda_agent]
Google search for        EDA on eBay DataFrame
card meta, set info,     (price stats, outliers,
recent trends            condition breakdown)
    │                          │
    └──────────────┬───────────┘
                   ▼
          [synthesis_agent]
          Combines context + EDA, produces
          buy/sell/hold recommendation
                   │
                   ▼
          [critique_agent]
          Flags low confidence, sparse data,
          or requests re-search if needed
```

**Agents to build:**

| Agent | File | Responsibility |
|---|---|---|
| `context_agent` | `src/agents/context_agent.py` | Google search for card set info, recent hype, population reports |
| `eda_agent` | `src/agents/eda_agent.py` | Statistical analysis of eBay DataFrame (mean, median, outliers, trend) |
| `synthesis_agent` | `src/agents/synthesis_agent.py` | Combines both agent outputs into a recommendation |
| `critique_agent` | `src/agents/critique_agent.py` | Validates synthesis output; flags uncertainty or requests more data |
| `orchestrator` | `src/orchestrator.py` | Coordinates all agents; manages parallel execution and handoffs |

**Why this pattern:**
This is an *orchestrated multi-agent pipeline* — parallel specialist agents feeding a single aggregator — not a fully autonomous agent network. That's intentional: the problem doesn't require agents to negotiate or spawn sub-agents dynamically. The complexity budget is kept low while still demonstrating real multi-agent coordination.

**New dependencies to add:**
- `pandas` / `scipy` — EDA in `eda_agent`
- `asyncio` — parallel agent execution

---

### Phase 3 — Quality & Robustness

- Add a confidence score to the synthesis output (e.g. "low confidence — only 3 sold listings found")
- `critique_agent` sends back to `context_agent` or `eda_agent` if data is insufficient (adds a feedback loop, making the system more genuinely multi-agent)
- Persist results to a local SQLite cache to avoid redundant SerpAPI calls
- Unit tests for `card_extractor` and `ebay_search` edge cases

---

### Phase 4 — Interface

- Wrap CLI in a simple web UI (FastAPI + minimal frontend) so non-technical users can query cards without a terminal
- Export recommendations as a formatted PDF or CSV report