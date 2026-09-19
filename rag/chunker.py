import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean unnecessary whitespace while preserving section structure.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Keep at most two consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split the knowledge base into meaningful chunks.

    The function tries to preserve headings and paragraphs so that
    related information stays together.
    """

    if not text.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    text = clean_text(text)

    # Split by blank lines first so sections remain meaningful.
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # If the paragraph fits into the current chunk
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:

            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

        else:
            # Save current chunk
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Handle very large paragraphs
            if len(paragraph) > chunk_size:

                start = 0

                while start < len(paragraph):

                    end = start + chunk_size

                    piece = paragraph[start:end].strip()

                    if piece:
                        chunks.append(piece)

                    start += chunk_size - chunk_overlap

                current_chunk = ""

            else:
                current_chunk = paragraph

    # Save final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


if __name__ == "__main__":

    from loader import load_document

    knowledge_base_path = "data/sakzs_restaurant.txt"

    text = load_document(knowledge_base_path)

    chunks = chunk_text(
        text,
        chunk_size=500,
        chunk_overlap=100
    )

    print("=" * 60)
    print("TEXT CHUNKING TEST")
    print("=" * 60)

    print(f"Original characters : {len(text):,}")
    print(f"Number of chunks    : {len(chunks)}")

    print("\n" + "=" * 60)
    print("CHUNKS")
    print("=" * 60)

    for index, chunk in enumerate(chunks, start=1):

        print(f"\n--- CHUNK {index} ---")
        print(f"Characters: {len(chunk)}")
        print(chunk)