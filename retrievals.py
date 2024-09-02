import numpy as np
from sentence_transformers import SentenceTransformer


class RetrievalSystem:
    def __init__(self, chunks, embeddings):
        self.chunks = chunks
        self.embeddings = embeddings
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve(self, query, top_k=5):
        """
        Retrieve the most relevant chunks for a given query.

        Args:
        query (str): The query to search for
        top_k (int): Number of top results to return

        Returns:
        list: List of tuples (chunk, similarity_score)
        """
        query_embedding = self.model.encode(query)

        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [(self.chunks[i], similarities[i]) for i in top_indices]
