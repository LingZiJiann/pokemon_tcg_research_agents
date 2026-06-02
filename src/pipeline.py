import asyncio

from .agents.eda_agent import EdaAgent
from .tools.card_extractor import extract_card_name
from .tools.ebay_search import EbaySearch
from .utils.logger import setup_logger


class Pipeline:
    def __init__(self):
        self._logger = setup_logger("pipeline", console_output=False)

    async def run(self, query: str) -> None:
        card_data = extract_card_name(query)
        print(f"\nExtracted Name: {card_data['name']}")
        print(f"Condition: {card_data['condition']}")
        print(f"\nSearching eBay for: {card_data['name']} ({card_data['condition']})")

        ebay_df = EbaySearch().search(card_data)

        print("\n" + "=" * 40)
        print("eBay Results:")
        print("=" * 40)
        if ebay_df.empty:
            print("No results found.")
            return
        print(ebay_df.to_string())

        print("\n" + "=" * 40)
        print("=== EDA Summary ===")
        print("=" * 40)
        eda_summary = await EdaAgent().run(ebay_df)
        print(eda_summary)
