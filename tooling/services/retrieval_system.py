import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from models import CodeLocation
from .query_preprocessing import QueryPreprocessor
from typing import List

class FAISSRetrievalSystem:
    def __init__(self, chunks=None, index_path=None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        if chunks:
            self.chunks = chunks
            self._build_index()
        elif index_path:
            self.load_index(index_path)
        self.query_preprocessor = QueryPreprocessor()

    def _build_index(self):
        texts = [
            f"File: {chunk['metadata']['file']}\n\n{' '.join(str(line) for line in chunk['content'])}"
            for chunk in self.chunks
        ]
        batch_size = 32
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = self.model.encode(batch, show_progress_bar=True)
            embeddings.extend(batch_embeddings)
        embeddings = np.array(embeddings).astype(np.float32)
        
        # Adjust the number of clusters based on the dataset size
        n_clusters = min(100, len(embeddings) // 2)  # Ensure at least 2 points per cluster
        
        quantizer = faiss.IndexFlatL2(self.dimension)
        self.index = faiss.IndexIVFFlat(quantizer, self.dimension, n_clusters)
        
        if len(embeddings) < n_clusters:
            # If we still don't have enough points, fall back to a simple IndexFlatL2
            print(f"Warning: Not enough data points ({len(embeddings)}) for IVF index. Using IndexFlatL2 instead.")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings)
        else:
            self.index.train(embeddings)
            self.index.add(embeddings)

    def save_index(self, filename):
        faiss.write_index(self.index, filename)
        np.save(filename + "_chunks.npy", self.chunks)

    def load_index(self, filename):
        self.index = faiss.read_index(filename)
        self.chunks = np.load(filename + "_chunks.npy", allow_pickle=True)

    def retrieve(self, query, top_k=5, similarity_threshold=0.1):
        query_embedding = self.model.encode([query]).astype(np.float32)
        distances, indices = self.index.search(query_embedding, top_k * 2)  # Retrieve more results initially

        results = []
        for i, idx in enumerate(indices[0]):
            distance = distances[0][i]
            similarity = 1 / (1 + distance)  # Convert distance to similarity score
            
            if similarity < similarity_threshold:
                continue  # Skip results below the threshold
            
            chunk = self.chunks[idx]
            results.append(
                CodeLocation(
                    file_path=chunk["metadata"]["file"],
                    start_line=chunk["metadata"]["start_line"],
                    end_line=chunk["metadata"]["end_line"],
                    score=similarity
                )
            )

            if len(results) == top_k:
                break  # Stop once we have enough results above the threshold

        return results

    def semantic_search(self, query: str, k: int = 5, similarity_threshold: float = 0.1) -> List[CodeLocation]:
        processed_query = self.query_preprocessor.preprocess(query)
        return self.retrieve(processed_query, k, similarity_threshold)
