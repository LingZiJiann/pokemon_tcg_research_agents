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
    if not results.empty:
        print(results.to_string())
    else:
        print("No results found.")



if __name__ == "__main__":
    main()
