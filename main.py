from src.tools.card_extractor import extract_card_name
from src.tools.ebay_search import EbaySearch
from src.utils.logger import setup_logger


def main():
    logger = setup_logger("main", console_output=False)

    print("Pokemon Card Research Agent")
    print("=" * 40)

    user_input = input("What card are you searching for? ").strip()
    if not user_input:
        print("No input provided. Exiting.")
        return

    logger.info(f"User query: {user_input}")

    extraction = extract_card_name(user_input)
    print(f"\nExtracted Name: {extraction['name']}")
    print(f"Condition: {extraction['condition']}")
    print(f"\nSearching for: {extraction['name']} ({extraction['condition']})")

    ebay_search = EbaySearch()
    results = ebay_search.search(extraction)

    print("\n" + "=" * 40)
    print("Search Results:")
    print("=" * 40)
    if results:
        for i, result in enumerate(results, 1):
            print(f"\n{i}. URL: {result.get('url', 'N/A')}")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Price: ${result.get('price', 'N/A')}")
            print(f"   Sold Date: {result.get('sold_date', 'N/A')}")
    else:
        print("No results found.")



if __name__ == "__main__":
    main()
