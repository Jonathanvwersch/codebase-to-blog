import os
import numpy as np
from sentence_transformers import SentenceTransformer

import torch
import faiss


class FAISSRetrievalSystem:
    def __init__(self, chunks=None, index_path=None):
        self.chunks = chunks
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        try:
            print("Loading model...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            # self.model = SentenceTransformer("dunzhang/stella_en_400M_v5", trust_remote_code=True)
            self.model = self.model.to(self.device)
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

        try:
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"Embedding dimension: {self.dimension}")
        except Exception as e:
            print(f"Error getting embedding dimension: {str(e)}")
            raise

        if index_path and os.path.exists(index_path):
            print(f"Loading index from {index_path}")
            self.load_index(index_path)
        else:
            print("Creating new index")
            self.index = faiss.IndexFlatL2(self.dimension)
            if chunks:
                self._build_index()

    def encode(self, texts):
        print(f"Encoding {len(texts)} texts")
        try:
            return self.model.encode(texts, show_progress_bar=True, device=self.device)
        except Exception as e:
            print(f"Error encoding texts: {str(e)}")
            raise

    def _build_index(self):
        print("Building index...")
        texts = [
            f"File: {chunk['metadata']['file']}\n\n{' '.join(str(line) for line in chunk['content'])}"
            for chunk in self.chunks
        ]
        batch_size = 32
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                batch_embeddings = self.encode(batch)
                embeddings.append(batch_embeddings)
            except Exception as e:
                print(f"Error encoding batch {i//batch_size}: {str(e)}")
                raise
        embeddings = np.vstack(embeddings)
        print(f"Adding {len(embeddings)} embeddings to index")
        self.index.add(embeddings.astype(np.float32))
        print("Index built")

    def retrieve(self, query, top_k=5):
        try:
            query_embedding = self.encode([query]).astype(np.float32)
            distances, indices = self.index.search(
                query_embedding, top_k * 2
            )  # Get more results initially

            results = []
            for i, idx in enumerate(indices[0]):
                chunk = self.chunks[idx]
                score = 1 / (
                    1 + distances[0][i]
                )  # Convert distance to similarity score

                # Apply a penalty to documentation files
                if chunk["metadata"]["file"].endswith((".md", ".rst", ".txt")):
                    score *= 0.5  # Reduce score for documentation files

                results.append(
                    {
                        "file_path": chunk["metadata"]["file"],
                        "start_line": chunk["metadata"]["start_line"],
                        "end_line": chunk["metadata"]["end_line"],
                        "score": score,
                    }
                )

            print("before sort", results)
            results.sort(key=lambda x: x["score"], reverse=True)
            print("after sort", results)
            return results[:5]
        except Exception as e:
            print(f"Error in retrieve: {str(e)}")
            raise

    def save_index(self, filename):
        try:
            print(f"Saving index to {filename}")
            faiss.write_index(self.index, filename)
            np.save(filename + "_chunks.npy", self.chunks)
            print("Index saved")
        except Exception as e:
            print(f"Error saving index: {str(e)}")
            raise

    def load_index(self, filename):
        try:
            print(f"Loading index from {filename}")
            self.index = faiss.read_index(filename)
            self.chunks = np.load(filename + "_chunks.npy", allow_pickle=True)
            print("Index loaded")
        except Exception as e:
            print(f"Error loading index: {str(e)}")
            raise
