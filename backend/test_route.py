import sys
import os
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
from app.agents.planner import _embeddings_model, _intent_vectors, cosine_similarity

q_vec = np.array(_embeddings_model.embed_query("Write a Python script to calculate the 100th number in the Fibonacci sequence and tell me what it is."))
scores = {k: max([cosine_similarity(q_vec, v) for v in vs]) for k, vs in _intent_vectors.items()}
print("Scores for the query:")
for k, v in scores.items():
    print(f"{k}: {v:.3f}")
