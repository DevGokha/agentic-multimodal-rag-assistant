import time
import logging
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

from app.services.memory import add_to_memory, get_memory
from app.agents.planner import decide_agent
from app.agents.tool import calculator_tool
from app.agents.web_search import web_search_tool
from app.agents.weather import extract_city, fetch_weather
from app.agents.finance import extract_ticker, fetch_stock_data
from app.agents.code_runner import generate_code, execute_code
from app.agents.image_gen import enhance_prompt, get_image_url
from app.agents.web_scraper import extract_url, scrape_website, summarize_page
from app.utils.rag import query_pdf

# Step 0: Create a logger for the orchestrator module
logger = logging.getLogger("orchestrator")

# --- LangGraph Setup ---

# 1. Define the State
class AgentState(TypedDict):
    query: str
    llm: Any
    agent_type: str
    response: Any
    memory_context: str

# 2. Define Nodes
def router_node(state: AgentState):
    agent_type = decide_agent(state["query"])
    return {"agent_type": agent_type}

def rag_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    try:
        context = query_pdf(query)
    except Exception:
        context = ""
    final_prompt = f"""You are a helpful AI assistant. You are given context from a document/PDF that the user just uploaded.
Answer the user's question based ONLY on the document context below. 
If the user asks about "the PDF", "the document", or "the file", they are explicitly referring to this document context. Do NOT say there is no PDF. Do NOT invent fake conversations.

Conversation History:
{state.get("memory_context", "")}

Document Context:
{context}

Question: {query}

Answer (keep it concise):"""
    response = llm.invoke(final_prompt)
    return {"response": response}

def web_search_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    search_results = web_search_tool(query)
    final_prompt = f"""You are a helpful AI assistant. The user asked a question and here are web search results.
Summarize the key information in a short, clear answer. Do NOT invent fake conversations.

Conversation History:
{state.get("memory_context", "")}

Web Search Results:
{search_results}

User Question: {query}

Answer (keep it concise):"""
    response = llm.invoke(final_prompt)
    return {"response": response}

def tool_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    response = calculator_tool(query, llm)
    return {"response": response}

def weather_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    
    city = extract_city(query, llm)
    weather_info = fetch_weather(city)
    
    final_prompt = f"""You are a helpful AI assistant. The user asked for the weather.
Use the provided weather information to give a short, friendly response.

Conversation History:
{state.get("memory_context", "")}

Weather Information:
{weather_info}

User Question: {query}

Answer (keep it concise):"""
    response = llm.invoke(final_prompt)
    return {"response": response}

def finance_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    
    ticker = extract_ticker(query, llm)
    stock_info = fetch_stock_data(ticker)
    
    final_prompt = f"""You are a helpful financial AI assistant. The user asked about a stock or the market.
Use the provided stock data to give a short, professional response.

Conversation History:
{state.get("memory_context", "")}

Stock Information:
{stock_info}

User Question: {query}

Answer (keep it concise):"""
    response = llm.invoke(final_prompt)
    return {"response": response}

def code_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    
    # 1. Ask LLM to generate the python code
    code_string = generate_code(query, llm)
    
    # 2. Execute the code safely
    execution_result = execute_code(code_string)
    
    # 3. Format the final output
    final_prompt = f"""You are a helpful AI assistant capable of writing and executing code.
The user asked a complex question requiring code execution. You generated a script and ran it.

User Question: {query}

Generated Code:
```python
{code_string}
```

Execution Output:
{execution_result}

Summarize the execution output and answer the user's question directly and concisely."""
    response = llm.invoke(final_prompt)
    return {"response": response}

def image_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    
    enhanced_prompt = enhance_prompt(query, llm)
    image_url = get_image_url(enhanced_prompt)
    
    # Return markdown image string that the frontend will render
    response = f"Here is your image:\n\n![{enhanced_prompt}]({image_url})"
    return {"response": response}

def web_scraper_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    
    url = extract_url(query)
    if not url:
        return {"response": "I couldn't find a valid web link in your message."}
        
    page_content = scrape_website(url)
    if not page_content:
        return {"response": "I couldn't retrieve or read the content from this website. It might be blocking scrapers."}
        
    summary = summarize_page(query, page_content, llm)
    return {"response": summary}

def default_llm_node(state: AgentState):
    query = state["query"]
    llm = state["llm"]
    final_prompt = f"""You are a friendly AI assistant. Give a short, helpful reply. Do NOT invent fake conversations.

Conversation History:
{state.get("memory_context", "")}

Question: {query}

Answer (keep it concise):"""
    response = llm.invoke(final_prompt)
    return {"response": response}

# 3. Build and Compile the Graph
def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("finance", finance_node)
    workflow.add_node("code", code_node)
    workflow.add_node("image", image_node)
    workflow.add_node("web_scraper", web_scraper_node)
    workflow.add_node("tool", tool_node)
    workflow.add_node("default_llm", default_llm_node)
    
    # Add start edge
    workflow.add_edge(START, "router")
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        lambda state: state["agent_type"],
        {
            "rag": "rag",
            "web_search": "web_search",
            "weather": "weather",
            "finance": "finance",
            "code": "code",
            "image": "image",
            "web_scraper": "web_scraper",
            "tool": "tool",
            "llm": "default_llm"
        }
    )
    
    # Add end edges
    workflow.add_edge("rag", END)
    workflow.add_edge("web_search", END)
    workflow.add_edge("weather", END)
    workflow.add_edge("finance", END)
    workflow.add_edge("code", END)
    workflow.add_edge("image", END)
    workflow.add_edge("web_scraper", END)
    workflow.add_edge("tool", END)
    workflow.add_edge("default_llm", END)
    
    return workflow.compile()

# Compile the graph once to be used by the run_agent function
agent_app = build_graph()

# --- Main Entry Point ---

async def run_agent(query, llm):
    # Step 0a: Record the start time to measure response latency
    start_time = time.time()

    memory = get_memory()
    memory_context = "\n".join(
        [f"User: {m['query']}\nAI: {m['response']}" for m in memory]
    )

    # Initialize state
    initial_state = {
        "query": query,
        "llm": llm,
        "agent_type": "",
        "response": None,
        "memory_context": memory_context
    }

    # Run LangGraph
    final_state = agent_app.invoke(initial_state)
    
    agent_type = final_state["agent_type"]
    response = final_state["response"]
    
    # EXTREME DEBUGGING
    logger.error(f"DEBUG: Input Query: {query}")
    logger.error(f"DEBUG: Agent Type Evaluated: {agent_type}")
    logger.error(f"DEBUG: Final Response: {response}")

    # Step 0b: Log which agent was selected for this query
    logger.info("Agent: %-12s | Query: %s", agent_type, query)

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