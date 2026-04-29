from src.utils.logger import setup_logger


def main():
    logger = setup_logger("main", console_output=False)

    print("Pokemon Card Research Agent")
    print("=" * 40)

    user_input = input("What card are you searching for? ").strip().lower()
    if not user_input:
        print("No input provided. Exiting.")
        return

    logger.info(f"User query: {user_input}")
    print(f"\nSearching for: {user_input}")


if __name__ == "__main__":
    main()
