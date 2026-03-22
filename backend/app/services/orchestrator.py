import time
import logging
from app.services.memory import add_to_memory, get_memory
from app.agents.planner import decide_agent
from app.agents.tool import calculator_tool
from app.agents.web_search import web_search_tool
from app.utils.rag import query_pdf

# Step 0: Create a logger for the orchestrator module
logger = logging.getLogger("orchestrator")

async def run_agent(query, llm):
    # Step 0a: Record the start time to measure response latency
    start_time = time.time()

    agent_type = decide_agent(query)
    # Step 0b: Log which agent was selected for this query
    logger.info("Agent: %-12s | Query: %s", agent_type, query)

    memory = get_memory()
    memory_context = "\n".join(
        [f"User: {m['query']}\nAI: {m['response']}" for m in memory]
    )

    if agent_type == "rag":
        # Step 1: Retrieve relevant context from the uploaded PDF via FAISS
        try:
            context = query_pdf(query)
        except Exception:
            context = ""
        final_prompt = f"""You are a helpful AI assistant. Answer the user's question in a short, clear paragraph.
Use ONLY the document context below if relevant. Do NOT invent fake conversations.

Document Context:
{context}

Question: {query}

Answer (keep it concise):"""
        response = llm.invoke(final_prompt)

    elif agent_type == "web_search":
        # Step 2: Fetch live web results and let the LLM summarize them
        search_results = web_search_tool(query)
        final_prompt = f"""You are a helpful AI assistant. The user asked a question and here are web search results.
Summarize the key information in a short, clear answer. Do NOT invent fake conversations.

Web Search Results:
{search_results}

User Question: {query}

Answer (keep it concise):"""
        response = llm.invoke(final_prompt)

    elif agent_type == "tool":
        response = calculator_tool(query)

    else:
        final_prompt = f"""You are a friendly AI assistant. Give a short, helpful reply. Do NOT invent fake conversations.

Question: {query}

Answer (keep it concise):"""
        response = llm.invoke(final_prompt)

    # Step 4: Extract text from LLM response
    #         ChatGroq returns an AIMessage object; Ollama returns a plain string
    if hasattr(response, "content"):
        response = response.content

    add_to_memory(query, response)

    # Step 5: Log the response time and a preview of the answer
    elapsed = time.time() - start_time
    preview = response[:80].replace("\n", " ") if response else ""
    logger.info("Agent: %-12s | Time: %.2fs | Response: %s...", agent_type, elapsed, preview)

    return response