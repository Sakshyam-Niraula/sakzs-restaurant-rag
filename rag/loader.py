from pathlib import Path
import pymupdf


SUPPORTED_EXTENSIONS = {".txt", ".pdf"}


def load_text_file(file_path: Path) -> str:
    """Load text from a .txt file."""
    return file_path.read_text(encoding="utf-8")


def load_pdf_file(file_path: Path) -> str:
    """Extract text from every page of a PDF."""
    text_parts = []

    with pymupdf.open(file_path) as document:
        for page in document:
            page_text = page.get_text()

            if page_text.strip():
                text_parts.append(page_text)

    return "\n".join(text_parts)


def load_document(file_path: str) -> str:
    """
    Load a supported knowledge-base document.

    Supported:
    - .txt
    - .pdf
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Knowledge-base file not found: {path}")

    extension = path.suffix.lower()

    if extension == ".txt":
        text = load_text_file(path)

    elif extension == ".pdf":
        text = load_pdf_file(path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    text = text.strip()

    if not text:
        raise ValueError(f"No readable text found in: {path}")

    return text


if __name__ == "__main__":
    knowledge_base = Path("data/sakzs_restaurant.txt")

    text = load_document(str(knowledge_base))

    print("=" * 60)
    print("KNOWLEDGE BASE LOADED SUCCESSFULLY")
    print("=" * 60)
    print(f"Characters: {len(text):,}")
    print(f"Words: {len(text.split()):,}")
    print()
    print("Preview:")
    print("-" * 60)
    print(text[:1000])
    print("-" * 60)