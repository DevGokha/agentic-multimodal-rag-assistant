from app.utils.rag import has_faiss_index

# Step 0: Keywords that indicate the user is asking about an uploaded PDF/document
RAG_KEYWORDS = {
    "pdf", "document", "file", "uploaded", "upload",
    "paper", "report", "notes", "syllabus",
    "in the pdf", "in the document", "in the file",
    "from the pdf", "from the document", "from the file",
    "according to the pdf", "according to the document",
    "based on the pdf", "based on the document",
    "what does the pdf say", "what does the document say",
}

# Step 0b: Keywords that indicate the user wants live web search results
SEARCH_KEYWORDS = {
    "search", "google", "look up", "find online",
    "search the web", "web search", "search online",
    "latest", "current", "recent news", "trending",
    "what is happening", "news about",
}

def decide_agent(query: str):
    query_lower = query.strip().lower()

    # Step 1: Tool condition — route math/calculation queries to the calculator
    if "calculate" in query_lower:
        return "tool"

    # Step 2: Web search condition — route to web search when user wants live info
    for keyword in SEARCH_KEYWORDS:
        if keyword in query_lower:
            return "web_search"

    # Step 3: RAG condition — only route to RAG if the user explicitly
    #         mentions the PDF/document AND a FAISS index exists
    if has_faiss_index():
        for keyword in RAG_KEYWORDS:
            if keyword in query_lower:
                return "rag"

    # Step 4: Default — use the Ollama LLM for all other queries
    return "llm"