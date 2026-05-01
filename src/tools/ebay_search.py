import os
from dotenv import load_dotenv
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
            List of dictionaries containing search results from SerpApi.
        """

        search_term = f"{card_data['name']} {card_data['condition']}"

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
            return [self._parse_listing(result) for result in results]
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
            "price": result.get("price", {}).get("extracted"),
            "sold_date": result.get("sold_date"),
        }