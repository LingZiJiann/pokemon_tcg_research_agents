from tavily import TavilyClient

from config.config import settings


def tavily_search_tool(
    query: str, max_results: int = 5, include_images: bool = False
) -> list[dict]:
    """Search the web using Tavily and return structured results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return. Defaults to 5.
        include_images: If True, appends image URLs from the response. Defaults to False.

    Returns:
        A list of dicts with keys ``title``, ``content``, and ``url`` for each
        result. If ``include_images`` is True, image entries contain only
        ``image_url``. On error, returns a single-element list with an ``error``
        key so callers (typically LLM agents) receive a readable failure message.
    """
    if not settings.tavily_api_key:
        raise ValueError("TAVILY_API_KEY not set in environment.")
    api_key = settings.tavily_api_key

    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query, max_results=max_results, include_images=include_images
        )

        results = []
        for r in response.get("results", []):
            results.append(
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                }
            )

        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})

        return results

    except Exception as e:
        return [{"error": str(e)}]  # For LLM-friendly agents
