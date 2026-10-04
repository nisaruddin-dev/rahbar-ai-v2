import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).parent
CHUNKS_PATH = BASE_DIR / "chunks.json"
INDEX_PATH = BASE_DIR / "faiss.index"
METADATA_PATH = BASE_DIR / "metadata.json"

MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list) or not chunks:
        raise ValueError("chunks.json is empty or invalid.")

    texts = [str(chunk.get("text", "")) for chunk in chunks]

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    metadata = []
    for i, chunk in enumerate(chunks):
        metadata.append({
            "vector_id": i,
            "text": chunk.get("text", ""),
            "metadata": chunk.get("metadata", {}),
        })

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Indexed {len(chunks)} chunks.")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print("FAISS index created successfully.")


if __name__ == "__main__":
    main()