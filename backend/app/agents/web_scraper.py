import re
import requests
from bs4 import BeautifulSoup
import logging
from langchain_core.prompts import PromptTemplate
from urllib.parse import urlparse

logger = logging.getLogger("web_scraper")

def extract_url(query: str) -> str:
    """Extracts the first HTTP/HTTPS URL found in the query."""
    match = re.search(r'(https?://[^\s]+)', query)
    if match:
        return match.group(1)
    return ""

def scrape_website(url: str) -> str:
    """Fetches and extracts readable text from a given URL."""
    try:
        # Add a common User-Agent to avoid being blocked by simple bot protection
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script, style, meta, noscript, and header/footer elements that usually contain junk
        for element in soup(["script", "style", "meta", "noscript", "header", "footer", "nav", "aside"]):
            element.decompose()

        # Extract text and collapse whitespace
        text = soup.get_text(separator=' ')
        # Collapse multiple spaces and newlines into single ones
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate text to roughly fit inside standard LLM context windows
        # Llama3-8b/70b has 8k token limit, so ~20k characters is very safe
        if len(clean_text) > 20000:
            clean_text = clean_text[:20000] + "\n\n[Content truncated due to length limits...]"
            
        return clean_text
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return ""

def summarize_page(query: str, page_content: str, llm) -> str:
    """Uses the LLM to summarize or answer questions based on the page content."""
    
    prompt = PromptTemplate.from_template(
        """You are an intelligent web reading assistant. The user provided a link to a website, and here is the text extracted from that page.

--- START OF PAGE CONTENT ---
{page_content}
--- END OF PAGE CONTENT ---

Based ONLY on the page content above, answer the user's question or summarize the main points if they just provided the link.

User Question/Input: {query}

Answer (keep it insightful and well-formatted):"""
    )
    
    # If the user only gave a raw URL without a question, inject a default prompt
    parsed_query = urlparse(query.strip())
    if parsed_query.scheme in ['http', 'https'] and parsed_query.netloc in query.strip() and len(query.strip().split()) == 1:
        query = "Please provide a comprehensive summary of this web page."

    chain = prompt | llm
    response = chain.invoke({"page_content": page_content, "query": query})
    return response
