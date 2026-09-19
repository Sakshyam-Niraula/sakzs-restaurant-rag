from typing import List
import os

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables from .env
load_dotenv()

MODEL_NAME = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


class EmbeddingModel:
    """Generate embeddings using the Gemini Embedding API."""

    def __init__(self, model_name: str = MODEL_NAME):
        print(f"Using embedding model: {model_name}")

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY was not found. "
                "Make sure your .env file contains GEMINI_API_KEY=your_key"
            )

        self.model_name = model_name

        self.client = genai.Client(
            api_key=api_key
        )

        print("Gemini embedding client initialized.")

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for knowledge-base documents.
        """

        if not texts:
            return np.empty(
                (0, EMBEDDING_DIMENSION),
                dtype="float32"
            )

        result = self.client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSION,
            ),
        )

        embeddings = [
            embedding.values
            for embedding in result.embeddings
        ]

        return np.asarray(
            embeddings,
            dtype="float32"
        )

    def encode_query(self, text: str) -> np.ndarray:
        """
        Generate an embedding for a user's search query.
        """

        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=EMBEDDING_DIMENSION,
            ),
        )

        return np.asarray(
            result.embeddings[0].values,
            dtype="float32"
        )


if __name__ == "__main__":
    from rag.loader import load_document
    from rag.chunker import chunk_text

    knowledge_base_path = "data/sakzs_restaurant.txt"

    print("=" * 60)
    print("GEMINI EMBEDDING TEST")
    print("=" * 60)

    # Load knowledge base
    text = load_document(knowledge_base_path)

    # Split into chunks
    chunks = chunk_text(
        text,
        chunk_size=500,
        chunk_overlap=100
    )

    print(f"Chunks found: {len(chunks)}")

    # Initialize embedding model
    embedding_model = EmbeddingModel()

    # Generate document embeddings
    embeddings = embedding_model.encode_documents(chunks)

    print("\n" + "=" * 60)
    print("EMBEDDINGS CREATED SUCCESSFULLY")
    print("=" * 60)

    print(f"Number of vectors : {embeddings.shape[0]}")
    print(f"Vector dimensions : {embeddings.shape[1]}")
    print(f"Data type         : {embeddings.dtype}")

    # Test query embedding
    query_embedding = embedding_model.encode_query(
        "How much does chicken momo cost?"
    )

    print(f"\nQuery vector dimensions: {query_embedding.shape[0]}")

    print("\n" + "=" * 60)
    print("GEMINI EMBEDDING TEST COMPLETED")
    print("=" * 60)