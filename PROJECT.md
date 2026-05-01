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
| `search_ebay_last_sold` | Queries SerpAPI eBay sold listings, returns top results with price and date |

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
- `python-dotenv` — load `.env`
