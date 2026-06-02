import asyncio

from src.orchestrator import Orchestrator


def main():
    print("Pokemon Card Research Agent")
    print("=" * 40)

    user_input = input("What card are you searching for? ").strip()
    if not user_input:
        print("No input provided. Exiting.")
        return

    asyncio.run(Orchestrator().run(user_input))


if __name__ == "__main__":
    main()
