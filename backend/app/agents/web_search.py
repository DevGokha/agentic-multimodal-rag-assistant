from ddgs import DDGS


def web_search_tool(query: str, max_results: int = 3):
    """
    Step 1: Search the web using DuckDuckGo (no API key needed).
    Returns a formatted string with the top search results including
    title, snippet, and URL for each result.
    """

    try:
        # Step 2: Run the DuckDuckGo text search
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        # Step 3: If no results found, return a friendly message
        if not results:
            return "No web results found for that query."

        # Step 4: Format each result as a readable block
        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            body = r.get("body", "No snippet")
            link = r.get("href", "")
            formatted.append(f"{i}. {title}\n   {body}\n   Source: {link}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Web search failed: {str(e)}"
