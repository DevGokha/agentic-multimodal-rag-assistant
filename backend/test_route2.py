import sys
from app.agents.planner import decide_agent

query = sys.argv[1]
agent = decide_agent(query)
print(f"Query: {query}")
print(f"Agent: {agent}")
