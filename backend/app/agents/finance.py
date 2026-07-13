import yfinance as yf
import logging
from typing import Any

logger = logging.getLogger("finance")

def extract_ticker(query: str, llm: Any) -> str:
    """Uses the LLM to extract the stock ticker symbol from the user's query."""
    prompt = f"""Extract the stock ticker symbol from the following query.
Convert company names to their official stock ticker symbol (e.g., Apple -> AAPL, Google -> GOOGL, Microsoft -> MSFT).
If no clear company or ticker is found, return 'Unknown'.
Return ONLY the uppercase ticker symbol, nothing else.
Query: {query}
Ticker:"""
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        ticker = content.strip().upper()
        
        # Remove any markdown formatting or punctuation
        ticker = ticker.replace('`', '').replace('.', '').replace(',', '').strip()
        
        if "UNKNOWN" in ticker or not ticker:
            return ""
        return ticker
    except Exception as e:
        logger.error(f"Error extracting ticker: {e}")
        return ""

def fetch_stock_data(ticker: str) -> str:
    """Fetches live stock data for the given ticker using yfinance."""
    if not ticker:
        return "No stock ticker provided or recognized."
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if hist.empty:
            return f"Could not fetch stock data for ticker: {ticker}. Please ensure it is a valid symbol."
            
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Open'].iloc[0] # Approximating previous close with today's open if needed, or we could fetch 2d.
        
        # Actually it's better to just get the latest close price and maybe high/low
        high = hist['High'].iloc[-1]
        low = hist['Low'].iloc[-1]
        
        # Try to get currency, default to USD
        currency = "USD"
        if hasattr(stock, 'info') and 'currency' in stock.info:
            currency = stock.info['currency']
            
        short_name = ticker
        if hasattr(stock, 'info') and 'shortName' in stock.info:
            short_name = stock.info['shortName']

        return (
            f"The current stock price of {short_name} ({ticker}) is {current_price:.2f} {currency}. "
            f"Today's High: {high:.2f} {currency}, Low: {low:.2f} {currency}."
        )
    except Exception as e:
        logger.error(f"Error fetching stock data for {ticker}: {e}")
        return f"Failed to fetch stock data for {ticker}. The symbol may be invalid or the service is temporarily unavailable."
