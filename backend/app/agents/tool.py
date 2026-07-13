import re
import ast
import operator
import logging

logger = logging.getLogger("calculator")

# Allowed operators for safe eval
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

def _safe_eval(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    else:
        raise TypeError(f"Unsupported operation: {type(node)}")

def calculator_tool(query: str, llm) -> str:
    try:
        # Use LLM to extract math expression
        prompt = f"""Extract ONLY the mathematical expression from the user's query. 
Convert words like 'divided by' into '/', 'times' into '*', etc.
Return ONLY the math expression (e.g., '150 / 3'). Do not include any other text.
Query: {query}
Expression:"""
        
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        expression = content.strip()
        
        # Strip backticks if the LLM wrapped it in code blocks
        expression = expression.replace('`', '').strip()

        if not expression:
            return "No valid calculation found."

        # Parse and safely evaluate
        node = ast.parse(expression, mode='eval').body
        result = _safe_eval(node)
        
        return f"Result: {result}"

    except Exception as e:
        logger.error("Calculator error on expression '%s': %s", locals().get('expression', 'None'), e)
        return "Sorry, I couldn't calculate that."