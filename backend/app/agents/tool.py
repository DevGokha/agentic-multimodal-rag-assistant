import re

def calculator_tool(query: str):
    try:
        # Extract math expression safely
        expression = re.sub(r"[^0-9+\-*/().]", "", query)

        if not expression:
            return "No valid calculation found."

        result = eval(expression)
        return f"Result: {result}"

    except Exception:
        return "Sorry, I couldn't calculate that."