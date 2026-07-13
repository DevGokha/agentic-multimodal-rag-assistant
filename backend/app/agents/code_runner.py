import os
import sys
import tempfile
import subprocess
import logging
import re
from typing import Any

logger = logging.getLogger("code_runner")

def generate_code(query: str, llm: Any) -> str:
    """Uses the LLM to write a purely functional Python script to solve the query."""
    prompt = f"""You are a Python programming expert. The user has asked a question that requires writing and running Python code to find the exact answer (e.g. data analysis, complex math, string manipulation, etc).

Write a standalone Python script to solve their problem. 
- You MUST print the final result using `print()`. Do not just return it.
- Do NOT use input(), interactive functions, or plotting functions that require a GUI (e.g. plt.show()).
- If you use libraries, assume `pandas`, `numpy`, `math` are available.

Return ONLY the Python code inside a markdown block. Do not include any explanations.

Query: {query}
"""
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        
        # Extract code from markdown blocks if present
        match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback to returning raw content (cleaning up backticks just in case)
        return content.replace('```python', '').replace('```', '').strip()
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        return ""

def execute_code(code_string: str) -> str:
    """Safely executes a Python script in a temporary file and captures the output."""
    if not code_string:
        return "No valid code generated to execute."
        
    temp_file = None
    try:
        # Create a temporary file
        fd, temp_file = tempfile.mkstemp(suffix=".py", text=True)
        with os.fdopen(fd, 'w') as f:
            f.write(code_string)
            
        # Execute the script using the current virtual environment Python
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=15.0 # Max 15 seconds to prevent infinite loops
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return f"Execution Output:\n{output}" if output else "Code executed successfully but returned no output."
        else:
            return f"Execution Error:\n{result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "Execution Error: The script took too long to run and timed out."
    except Exception as e:
        logger.error(f"Failed to execute code: {e}")
        return f"System Error executing code: {str(e)}"
    finally:
        # Clean up the temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.error(f"Failed to delete temp file {temp_file}: {e}")
