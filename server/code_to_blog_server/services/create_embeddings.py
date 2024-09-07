import numpy as np
from sentence_transformers import SentenceTransformer


def create_embeddings(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = []
    for chunk in chunks:
        text_to_embed = f"File: {chunk['metadata']['file']}\n\n{chunk['content']}"
        embedding = model.encode(text_to_embed)
        embeddings.append(embedding)
    return np.array(embeddings)
