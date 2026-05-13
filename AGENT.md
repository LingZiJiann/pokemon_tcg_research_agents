# Multi-Agent Pipeline — Implementation Plan

## Architecture

```
User Input
    ↓
extract_card_name()              ← plain Python (no agent)
    ↓
EbaySearch().search()            ← plain Python (no agent)
    ↓
asyncio.gather(
  eda_agent.run(ebay_df)         ← Phase 1
  research_pipeline.run(card)    ← Phase 2
    → 3 concurrent search agents (Tavily)
    → consolidation_agent
)
    ↓
analyst_agent.run(...)           ← Phase 3
    ↓
Print formatted recommendation
```

---

## Phase 1 — EDA Agent

**Goal:** Interpret the eBay DataFrame with a Claude agent and surface key pricing signals.

### Config changes (`config/config.py`)
- Add `anthropic_api_key: str = ""` — reads `ANTHROPIC_API_KEY` from `.env`
- Add `anthropic_model: str = "claude-sonnet-4-6"` — shared by all agents

### New file: `src/agents/eda_agent.py`

`EdaAgent.run(ebay_df: pd.DataFrame) -> str`

1. **Python computes stats** (no Claude yet):
   - `count`, `mean`, `median`, `std`, `min`, `max`
   - IQR-based outlier detection
   - Date range of listings
2. **Single Claude call** (`AsyncAnthropic`, no tools):
   - System: "You are a data analyst specialising in Pokemon card pricing."
   - User message: structured stats block + raw price list
   - Returns Claude's plain-language interpretation

### New file: `src/orchestrator.py` (skeleton)

`Orchestrator.run(query: str) -> None` (async)

At end of Phase 1 it runs:
```
extract_card_name → EbaySearch.search → eda_agent.run → print EDA output
```

### Update `main.py`
- Replace direct tool calls with `asyncio.run(Orchestrator().run(user_input))`

---

## Phase 2 — Research Pipeline

**Goal:** Spawn 3 concurrent Tavily search agents and consolidate results into a market overview.

### New file: `src/agents/search_agent.py`

`SearchAgent.run(query: str) -> dict`

- Calls `tavily_search_tool(query)` directly from `src/tools/research_tools.py`
- Returns `{"query": query, "results": [...]}`
- No Claude call — pure tool invocation
- Used 3× concurrently:
  - `"{card} {condition} investment"`
  - `"{card} {condition} reddit"`
  - `"{card} {condition} pricecharting"`

### New file: `src/agents/consolidation_agent.py`

`ConsolidationAgent.run(search_results: list[dict]) -> str`

- Single Claude call, no tools
- System: "You are a Pokemon card market researcher. Consolidate the following search results into a concise overview covering investment outlook, community sentiment, and historical pricing."
- User message: all 3 search results formatted as a block
- Returns the overview text

### Update `src/orchestrator.py`

Add `_research_pipeline(card_data)` async helper:
```python
results = await asyncio.gather(
    SearchAgent().run(f"{name} {condition} investment"),
    SearchAgent().run(f"{name} {condition} reddit"),
    SearchAgent().run(f"{name} {condition} pricecharting"),
)
overview = await ConsolidationAgent().run(results)
return overview
```

Update `Orchestrator.run` to run EDA + research pipeline concurrently:
```python
eda_summary, overview = await asyncio.gather(
    eda_agent.run(ebay_df),
    self._research_pipeline(card_data),
)
```

---

## Phase 3 — Analyst Agent & Final Output

**Goal:** Combine EDA and research overview into a final buy/hold/sell recommendation.

### New file: `src/agents/analyst_agent.py`

`AnalystAgent.run(card_data: dict, eda_summary: str, overview: str) -> str`

- Single Claude call, no tools
- System: "You are a Pokemon card investment analyst. Based on the data provided, give a clear buy / hold / sell recommendation with concise reasoning."
- User message: card name + condition, EDA summary, market overview
- Returns the final recommendation

### Complete `src/orchestrator.py`

Wire in the analyst agent after Phase 2 completes:
```python
recommendation = await AnalystAgent().run(card_data, eda_summary, overview)
```

Print all sections with clear headers:
```
=== EDA Summary ===
...

=== Market Overview ===
...

=== Analyst Recommendation ===
...
```

---

## Files Summary

| File | Action | Phase |
|---|---|---|
| `config/config.py` | Add `anthropic_api_key`, `anthropic_model` | 1 |
| `src/agents/eda_agent.py` | Create | 1 |
| `src/orchestrator.py` | Create (skeleton → complete) | 1–3 |
| `main.py` | Update to use orchestrator | 1 |
| `src/agents/search_agent.py` | Create | 2 |
| `src/agents/consolidation_agent.py` | Create | 2 |
| `src/agents/analyst_agent.py` | Create | 3 |

**Unchanged:** `card_extractor.py`, `ebay_search.py`, `research_tools.py`, `logger.py`, `research_agent.py`
