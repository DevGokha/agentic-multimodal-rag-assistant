import sys
from app.services.orchestrator import run_agent
from app.config import llm

query = sys.argv[1]
response = run_agent(query, llm)
print(f"Final Response: {response}")
