import os

from dotenv import load_dotenv
from rapidfuzz import fuzz
import serpapi

from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("ebay_search")

class EbaySearch:
    
    SHOW_ONLY = "Sold"
    BUYING_FORMAT = "Auction"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not provided and not in environment")

    def search(self, card_data: dict) -> list[dict]:
        """Search eBay for a card based on card extractor results.

        Args:
            card_data: Dictionary with 'name' and 'condition' keys from card_extractor.

        Returns:
            List of dictionaries containing search results from SerpApi filtered by condition.
        """

        search_term = f"{card_data['name']} {card_data['condition']}"
        condition = card_data['condition']

        params = {
            "engine": "ebay",
            "_nkw": search_term,
            "show_only": self.SHOW_ONLY,
            "buying_format": self.BUYING_FORMAT,
        }

        try:
            client = serpapi.Client(api_key=self.api_key)
            results = client.search(params)
            results = results.get("organic_results", [])
            logger.info(f"eBay search completed for: {search_term}")

            parsed_results = [self._parse_listing(result) for result in results]
            filtered_results = self._filter_and_rank(parsed_results, condition, search_term)

            logger.info(f"Filtered {len(parsed_results)} results to {len(filtered_results)} matching condition '{condition}'")
            return filtered_results
        except Exception as e:
            logger.error(f"eBay search failed for '{search_term}': {str(e)}")
            raise

    def _parse_listing(self, result: dict) -> dict:
        """Extract relevant fields from a raw SerpAPI listing result.

        Args:
            result: A single organic result dict from SerpAPI.

        Returns:
            A dict with url, price, and sold_date.
        """
        return {
            "url": result.get("link"),
            "title": result.get("title"),
            "price": result.get("price", {}).get("extracted"),
            "sold_date": result.get("sold_date"),
        }

    def _filter_and_rank(self, results: list[dict], condition: str, search_term: str) -> list[dict]:
        filtered = [
            {**r, "score": fuzz.token_set_ratio(search_term, r["title"] or "")}
            for r in results
            if self._title_contains_condition(r["title"], condition)
        ]
        return sorted(filtered, key=lambda r: r["score"], reverse=True)

    def _title_contains_condition(self, title: str, condition: str) -> bool:
        """Check if title contains the specified card condition.

        Args:
            title: The listing title to check.
            condition: The card condition to look for (e.g., 'NM', 'LP', 'MP', 'HP', 'DMG').

        Returns:
            True if the title contains the condition, False otherwise.
        """
        if not title:
            return False
        return condition.lower() in title.lower()
    