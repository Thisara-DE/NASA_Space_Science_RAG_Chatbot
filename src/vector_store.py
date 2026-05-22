import os
import pandas as pd
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.join(os.path.dirname(__file__), '..')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
QA_CSV        = os.path.join(BASE_DIR, 'data', 'qa_dataset.csv')
CHROMA_DIR    = os.path.join(BASE_DIR, 'data', 'chroma_db')
os.makedirs(CHROMA_DIR, exist_ok=True)

# ── Embedding model (runs locally, no API key needed) ──────────────────────────
EMBED_MODEL = "all-MiniLM-L6-v2"

# ── ChromaDB collection names ──────────────────────────────────────────────────
DOCS_COLLECTION = "nasa_documents"   # chunked raw pages
QA_COLLECTION   = "nasa_qa_pairs"    # Q&A dataset


def get_chroma_client():
    """Create a persistent ChromaDB client that saves to data/chroma_db/."""
    return PersistentClient(path=CHROMA_DIR)


def get_embedding_function():
    """Load the sentence-transformer embedding model."""
    return SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)


def build_document_store(client, embed_fn) -> int:
    """
    Chunk all processed .txt files and store them in ChromaDB.
    Returns the number of chunks stored.
    """
    print("\n📄 Building document store from scraped pages...")

    # Delete existing collection so we start fresh each run
    try:
        client.delete_collection(DOCS_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=DOCS_COLLECTION,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Text splitter — 500 char chunks, 50 char overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "],
    )

    documents, metadatas, ids = [], [], []
    chunk_index = 0

    txt_files = [f for f in sorted(os.listdir(PROCESSED_DIR)) if f.endswith(".txt")]

    for filename in txt_files:
        filepath = os.path.join(PROCESSED_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse header
        lines = content.splitlines()
        url   = lines[0].replace("URL: ", "").strip()   if lines else ""
        title = lines[1].replace("TITLE: ", "").strip() if len(lines) > 1 else filename
        text  = "\n".join(lines[3:]).strip()

        if not text:
            continue

        chunks = splitter.split_text(text)

        for chunk in chunks:
            if len(chunk.strip()) < 50:   # skip tiny fragments
                continue
            documents.append(chunk)
            metadatas.append({"source": url, "title": title, "filename": filename})
            ids.append(f"doc_{chunk_index}")
            chunk_index += 1

        print(f"  ✓ {filename[:45]:<45} → {len(chunks)} chunks")

    # Add to ChromaDB in one batch
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"\n  📦 Total chunks stored: {chunk_index}")
    return chunk_index


def build_qa_store(client, embed_fn) -> int:
    """
    Load qa_dataset.csv and store each question+answer in ChromaDB.
    Returns the number of Q&A pairs stored.
    """
    print("\n💬 Building Q&A store from qa_dataset.csv...")

    try:
        client.delete_collection(QA_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=QA_COLLECTION,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    df = pd.read_csv(QA_CSV)
    df = df.dropna(subset=["question", "answer"])   # drop any empty rows

    documents, metadatas, ids = [], [], []

    for i, row in df.iterrows():
        # We embed the QUESTION so similarity search matches user queries
        documents.append(str(row["question"]))
        metadatas.append({
            "answer":       str(row["answer"]),
            "source_page":  str(row.get("source_page", "")),
            "source_title": str(row.get("source_title", "")),
        })
        ids.append(f"qa_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"  ✓ Stored {len(documents)} Q&A pairs")
    return len(documents)


def verify_stores(client, embed_fn) -> None:
    """Run a quick test search on both collections to verify everything works."""
    print("\n🔍 Verifying stores with a test query...")
    test_query = "What is the surface of Mars like?"

    # Test document store
    doc_col = client.get_collection(DOCS_COLLECTION, embedding_function=embed_fn)
    doc_results = doc_col.query(query_texts=[test_query], n_results=2)
    print(f"\n  Test query: '{test_query}'")
    print(f"  Document store — top result:")
    if doc_results["documents"][0]:
        print(f"    \"{doc_results['documents'][0][0][:120]}...\"")

    # Test Q&A store
    qa_col = client.get_collection(QA_COLLECTION, embedding_function=embed_fn)
    qa_results = qa_col.query(query_texts=[test_query], n_results=2)
    print(f"  Q&A store — top matching question:")
    if qa_results["documents"][0]:
        print(f"    Q: \"{qa_results['documents'][0][0]}\"")
        print(f"    A: \"{qa_results['metadatas'][0][0]['answer'][:120]}...\"")


def main():
    print("🧠 NASA Vector Store Builder")
    print(f"   Embedding model : {EMBED_MODEL}")
    print(f"   Storage location: data/chroma_db/")
    print("=" * 50)

    embed_fn = get_embedding_function()
    client   = get_chroma_client()

    doc_count = build_document_store(client, embed_fn)
    qa_count  = build_qa_store(client, embed_fn)

    verify_stores(client, embed_fn)

    print("\n" + "=" * 50)
    print(f"✅ Vector store ready!")
    print(f"   Document chunks : {doc_count}")
    print(f"   Q&A pairs       : {qa_count}")
    print(f"   Saved to        : data/chroma_db/")


if __name__ == "__main__":
    main()