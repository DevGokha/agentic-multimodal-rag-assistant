import numpy as np
from app.utils.rag import has_faiss_index
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import logging

logger = logging.getLogger("planner")

# 1. Define Example Intent Phrases
INTENT_PHRASES = {
    "tool": [
        "calculate this",
        "what is the math",
        "solve this equation",
        "calculate 25 * 4 + 10",
        "calculate the square root",
        "do the math"
    ],
    "web_search": [
        "search the web",
        "latest news",
        "current events",
        "what is happening today",
        "find online resources",
        "search latest AI trends",
        "What is the latest news about Python?",
        "What is currently trending in tech?",
        "search google"
    ],
    "weather": [
        "what is the weather like",
        "temperature outside",
        "is it raining in",
        "weather forecast",
        "how cold is it in",
        "is it sunny in",
        "weather right now"
    ],
    "finance": [
        "stock price",
        "market cap",
        "finance news",
        "current price of",
        "how is the stock market",
        "share price"
    ],
    "code": [
        "write a python script",
        "generate the fibonacci sequence in python",
        "write code to solve this",
        "data analysis",
        "use python to compute",
        "write a script that"
    ],
    "image": [
        "generate an image",
        "draw a picture of",
        "create art",
        "show me an image of",
        "make a picture of",
        "render a 3d model of"
    ],
    "youtube": [
        "summarize this youtube video",
        "what is this video about",
        "explain the youtube link",
        "what does this youtube video say",
        "summarize the video at"
    ],
    "web_scraper": [
        "summarize this article",
        "read this webpage",
        "scrape this website",
        "what does this web page say",
        "summarize the link",
        "extract text from this link",
        "what is the article about"
    ],
    "rag": [
        "summarize the document",
        "what does the pdf say",
        "analyze the uploaded file",
        "from the notes",
        "According to the pdf",
        "Explain the notes on page 5",
        "What is in the uploaded file?",
        "what does the document say"
    ],
    "llm": [
        "hello",
        "hi",
        "how are you",
        "tell me a joke",
        "what is machine learning",
        "How does gravity work?",
        "write a poem",
        "explain to me",
        "what is the capital of",
        "who is the president",
        "where is this located",
        "when did this happen",
        "can you answer a general question",
        "tell me about history or geography",
        "what does this mean"
    ]
}

# 2. Initialize the Embedding Model
logger.info("Loading embedding model for Semantic Routing...")
_embeddings_model = FastEmbedEmbeddings()

# 3. Pre-compute embeddings for all intent phrases
_intent_vectors = {}
for intent, phrases in INTENT_PHRASES.items():
    # embed_documents takes a list of strings and returns a list of vectors
    vectors = _embeddings_model.embed_documents(phrases)
    _intent_vectors[intent] = np.array(vectors)
logger.info("Semantic Routing model ready.")

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def decide_agent(query: str):
    query_lower = query.strip().lower()

    # Fast-path for explicit YouTube URLs
    if "youtube.com/watch" in query_lower or "youtu.be/" in query_lower:
        return "youtube"
        
    # Fast-path for other web URLs
    if "http://" in query_lower or "https://" in query_lower:
        return "web_scraper"

    # Embed the user's query
    query_vector = np.array(_embeddings_model.embed_query(query_lower))

    best_intent = "llm"
    highest_score = -1.0

    # Calculate similarity against all intents
    for intent, vectors in _intent_vectors.items():
        for vec in vectors:
            score = cosine_similarity(query_vector, vec)
            if score > highest_score:
                highest_score = score
                best_intent = intent

    # Log the similarity result for debugging
    logger.info("Semantic Match: %s (Score: %.2f)", best_intent, highest_score)

    # Threshold fallback — if confidence is too low, route to llm to prevent random tools
    if highest_score < 0.28:
        logger.info("Score below threshold (0.28). Routing to llm.")
        return "llm"

    # RAG condition — fallback to llm if no FAISS index exists
    if best_intent == "rag" and not has_faiss_index():
        return "llm"

    return best_intent