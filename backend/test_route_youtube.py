import sys
from app.agents.planner import decide_agent

query = "https://www.youtube.com/watch?v=bP8ATWCvqzw&list=RD9T-Zbxg9X_4&index=2"
agent = decide_agent(query)
print(f"Query: {query}")
print(f"Agent: {agent}")
