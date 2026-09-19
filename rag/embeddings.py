from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


# Lightweight and reliable general-purpose embedding model.
MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingModel:
    """Generate vector embeddings for text."""

    def __init__(self, model_name: str = MODEL_NAME):
        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        print("Embedding model loaded successfully.")

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of text chunks into numerical vectors.
        """
        if not texts:
            return np.empty((0, 384), dtype="float32")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.astype("float32")


if __name__ == "__main__":
    from loader import load_document
    from chunker import chunk_text

    knowledge_base_path = "data/sakzs_restaurant.txt"

    # 1. Load knowledge base
    text = load_document(knowledge_base_path)

    # 2. Split into chunks
    chunks = chunk_text(
        text,
        chunk_size=500,
        chunk_overlap=100
    )

    print("=" * 60)
    print("EMBEDDING TEST")
    print("=" * 60)

    print(f"Chunks found: {len(chunks)}")

    # 3. Load embedding model
    embedding_model = EmbeddingModel()

    # 4. Generate embeddings
    embeddings = embedding_model.encode(chunks)

    print("\n" + "=" * 60)
    print("EMBEDDINGS CREATED SUCCESSFULLY")
    print("=" * 60)

    print(f"Number of vectors : {embeddings.shape[0]}")
    print(f"Vector dimensions : {embeddings.shape[1]}")
    print(f"Data type         : {embeddings.dtype}")

    print("\nFirst vector preview:")
    print(embeddings[0][:10])