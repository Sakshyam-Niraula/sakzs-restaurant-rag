from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np

from .loader import load_document
from .chunker import chunk_text
from .embeddings import EmbeddingModel


KNOWLEDGE_BASE = "data/sakzs_restaurant.txt"

INDEX_DIR = Path("data/vector_store")
INDEX_FILE = INDEX_DIR / "sakzs.index"
CHUNKS_FILE = INDEX_DIR / "chunks.txt"

TOP_K = 3


class FAISSStore:
    """Store and retrieve restaurant knowledge using FAISS."""

    def __init__(self):
        self.index = None
        self.chunks: List[str] = []

        self.load()

    def build(self, chunks: List[str]) -> None:
        """Create a FAISS index from text chunks."""

        if not chunks:
            raise ValueError("Cannot build FAISS index with no chunks.")

        print("\nGenerating embeddings...")

        embedding_model = EmbeddingModel()
        embeddings = embedding_model.encode(chunks)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        self.chunks = chunks

        print("\nFAISS index created successfully.")
        print(f"Vectors stored : {self.index.ntotal}")
        print(f"Vector size    : {dimension}")

    def save(self) -> None:
        """Save FAISS index and chunks to disk."""

        if self.index is None:
            raise RuntimeError("Cannot save an empty FAISS index.")

        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(INDEX_FILE)
        )

        with open(CHUNKS_FILE, "w", encoding="utf-8") as file:
            for chunk in self.chunks:
                file.write(
                    chunk.replace("\n", " ")
                    + "\n---CHUNK---\n"
                )

        print("\nVector store saved.")
        print(f"Index : {INDEX_FILE}")
        print(f"Chunks: {CHUNKS_FILE}")

    def load(self) -> None:
        """Load the existing FAISS vector store."""

        if not INDEX_FILE.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {INDEX_FILE}. "
                "Build the vector store first."
            )

        if not CHUNKS_FILE.exists():
            raise FileNotFoundError(
                f"Chunks file not found: {CHUNKS_FILE}. "
                "Build the vector store first."
            )

        self.index = faiss.read_index(
            str(INDEX_FILE)
        )

        with open(
            CHUNKS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        self.chunks = [
            chunk.strip()
            for chunk in content.split("---CHUNK---")
            if chunk.strip()
        ]

        if self.index.ntotal != len(self.chunks):
            raise RuntimeError(
                "FAISS index and chunks file are out of sync. "
                f"Vectors: {self.index.ntotal}, "
                f"Chunks: {len(self.chunks)}"
            )

        print("\nVector store loaded successfully.")
        print(f"Vectors: {self.index.ntotal}")
        print(f"Chunks : {len(self.chunks)}")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = TOP_K
    ) -> List[Dict]:
        """
        Search the vector database using a query embedding.

        Returns:
            List of dictionaries containing chunk and similarity score.
        """

        if self.index is None:
            raise RuntimeError(
                "FAISS index has not been built or loaded."
            )

        if query_embedding is None:
            return []

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if query_embedding.shape[1] != self.index.d:
            raise ValueError(
                "Query embedding dimension does not match "
                f"FAISS index dimension. "
                f"Query: {query_embedding.shape[1]}, "
                f"Index: {self.index.d}"
            )

        limit = min(top_k, self.index.ntotal)

        if limit <= 0:
            return []

        scores, indices = self.index.search(
            query_embedding,
            limit
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):
            if index == -1:
                continue

            results.append(
                {
                    "chunk": self.chunks[index],
                    "score": float(score)
                }
            )

        return results


if __name__ == "__main__":

    print("=" * 60)
    print("SAKZ'S RESTAURANT - FAISS VECTOR STORE")
    print("=" * 60)

    print("\nLoading knowledge base...")

    text = load_document(KNOWLEDGE_BASE)

    print(f"Characters loaded: {len(text):,}")

    print("\nCreating chunks...")

    chunks = chunk_text(
        text,
        chunk_size=500,
        chunk_overlap=100
    )

    print(f"Chunks created: {len(chunks)}")

    store = FAISSStore()

    store.build(chunks)
    store.save()

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)

    test_questions = [
        "How much does chicken momo cost?",
        "What time does the restaurant close on Saturday?",
        "Do you accept eSewa?"
    ]

    embedding_model = EmbeddingModel()

    for question in test_questions:

        print("\n" + "-" * 60)
        print(f"QUESTION: {question}")
        print("-" * 60)

        query_embedding = embedding_model.encode(
            [question]
        )

        results = store.search(
            query_embedding[0],
            top_k=3
        )

        for number, result in enumerate(
            results,
            start=1
        ):
            print(f"\nResult {number}")
            print(
                f"Similarity: {result['score']:.4f}"
            )
            print(result["chunk"])