import re
from typing import List, Dict

from rag.embeddings import EmbeddingModel
from rag.faiss_store import FAISSStore
from rag.gemini_client import GeminiClient


TOP_K = 3
MENU_TOP_K = 6
SIMILARITY_THRESHOLD = 0.15

STOP_WORDS = {
    "the", "is", "are", "a", "an", "and", "or", "of", "to", "in",
    "on", "for", "with", "do", "does", "did", "have", "has", "can",
    "could", "would", "what", "which", "where", "when", "how", "much",
    "many", "me", "tell", "please", "there", "restaurant", "sakz",
    "sakzs"
}

UNAVAILABLE_TERMS = {
    "swimming pool",
    "hotel room",
    "hotel rooms",
    "catering",
    "pet policy",
    "pet policies",
    "parking",
    "wi-fi",
    "wifi",
    "accessibility",
    "nutrition",
    "allergens",
    "ingredients",
    "franchise",
    "franchises",
    "jobs"
}


SYSTEM_INSTRUCTION = """
You are the customer-service assistant for Sakz's Restaurant.

IMPORTANT RULES:

1. Answer ONLY using the supplied restaurant knowledge base.
2. Never invent, guess, or assume information.
3. If the requested information is not available in the knowledge base,
   clearly say that the information is not available.
4. Do not use outside knowledge.
5. Keep answers concise and helpful.
6. When useful, mention the relevant source section.
"""


class RAGPipeline:

    def __init__(self):
        print("Initializing RAG pipeline...")

        self.embedding_model = EmbeddingModel()
        self.vector_store = FAISSStore()
        self.gemini = GeminiClient()

        print("RAG pipeline initialized successfully.")

    def retrieve(self, question: str, top_k: int = TOP_K) -> List[Dict]:
        question_embedding = self.embedding_model.encode_query(question)

        results = self.vector_store.search(
            question_embedding,
            top_k=top_k
        )

        return results

    def get_menu_chunks(self) -> List[Dict]:
        menu_queries = [
            "menu starters main course pizza burgers desserts beverages prices",
            "food drinks prices menu"
        ]

        all_results = []

        for query in menu_queries:
            results = self.retrieve(query, top_k=MENU_TOP_K)
            all_results.extend(results)

        unique = {}

        for result in all_results:
            chunk = result.get("chunk", "")
            unique[chunk] = result

        return list(unique.values())

    def is_menu_overview_query(self, question: str) -> bool:
        q = question.lower().strip()

        menu_phrases = [
            "menu",
            "menus",
            "what food",
            "what foods",
            "food do you have",
            "food available",
            "what do you serve",
            "what can i order",
            "what can we order",
            "list the food",
            "list all food",
            "show me the menu",
            "show menu"
        ]

        return any(phrase in q for phrase in menu_phrases)

    def extract_query_terms(self, question: str) -> List[str]:
        words = re.findall(
            r"[a-zA-Z0-9]+",
            question.lower()
        )

        terms = []

        for word in words:
            if len(word) > 2 and word not in STOP_WORDS:
                terms.append(word)

        return terms

    def requested_unavailable_item(self, question: str) -> bool:
        q = question.lower()

        for term in UNAVAILABLE_TERMS:
            if term in q:
                return True

        return False

    def has_query_evidence(
        self,
        question: str,
        results: List[Dict]
    ) -> bool:

        terms = self.extract_query_terms(question)

        if not terms:
            return False

        valid_chunks = []

        for result in results:
            chunk = result.get("chunk", "")
            lower_chunk = chunk.lower()

            if (
                "information not provided" in lower_chunk
                or "not provided" in lower_chunk
                or "information unavailable" in lower_chunk
            ):
                continue

            valid_chunks.append(lower_chunk)

        combined_context = " ".join(valid_chunks)

        matched_terms = []

        for term in terms:
            if term in combined_context:
                matched_terms.append(term)

        print("Query evidence:", matched_terms)

        return len(matched_terms) > 0

    def is_relevant(
        self,
        question: str,
        results: List[Dict]
    ) -> bool:

        if self.requested_unavailable_item(question):
            print("Requested item is explicitly unavailable in the KB.")
            return False

        if not results:
            print("No retrieval results.")
            return False

        best_score = results[0].get("score", 0)

        print(
            "Best similarity score:",
            round(float(best_score), 4)
        )

        if best_score < SIMILARITY_THRESHOLD:
            print("Similarity below threshold.")
            return False

        if not self.has_query_evidence(question, results):
            print("No valid query evidence found.")
            return False

        return True

    def build_context(self, results: List[Dict]) -> str:
        context_parts = []

        for i, result in enumerate(results, start=1):
            chunk = result.get("chunk", "")
            score = result.get("score", 0)

            context_parts.append(
                f"[Source {i} | similarity={score:.4f}]\n{chunk}"
            )

        return "\n\n".join(context_parts)

    def answer(self, question: str) -> Dict:

        question = question.strip()

        if not question:
            return {
                "answer": "Please enter a question.",
                "grounded": False,
                "sources": []
            }

        if self.is_menu_overview_query(question):
            results = self.get_menu_chunks()
        else:
            results = self.retrieve(
                question,
                top_k=TOP_K
            )

        if self.requested_unavailable_item(question):
            return {
                "answer": (
                    "Sorry, that information is not available "
                    "in Sakz's Restaurant's knowledge base."
                ),
                "grounded": False,
                "sources": results
            }

        if not self.is_relevant(question, results):
            return {
                "answer": (
                    "Sorry, that information is not available "
                    "in Sakz's Restaurant's knowledge base."
                ),
                "grounded": False,
                "sources": results
            }

        context = self.build_context(results)

        prompt = f"""
{SYSTEM_INSTRUCTION}

KNOWLEDGE BASE CONTEXT:
{context}

USER QUESTION:
{question}

Answer the user's question using ONLY the knowledge base context above.

If the answer cannot be found in the context, say:

"Sorry, that information is not available in Sakz's Restaurant's knowledge base."

Do not guess or add information from outside the knowledge base.
"""

        try:
            response = self.gemini.generate(prompt)

            return {
                "answer": response,
                "grounded": True,
                "sources": results
            }

        except Exception as e:
            print("Gemini error:", e)

            return {
                "answer": (
                    "The restaurant information service is temporarily "
                    "unavailable. Please try again later."
                ),
                "grounded": False,
                "sources": results
            }


if __name__ == "__main__":

    pipeline = RAGPipeline()

    question = "Does Sakz's Restaurant have a swimming pool?"

    result = pipeline.answer(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nGROUNDED:")
    print(result["grounded"])