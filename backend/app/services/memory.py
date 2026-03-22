chat_history = []

def add_to_memory(query, response):
    chat_history.append({
        "query": query,
        "response": response
    })

def get_memory():
    return chat_history[-5:]  # last 5 messages