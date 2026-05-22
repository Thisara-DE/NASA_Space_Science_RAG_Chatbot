import os
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ── Paths & config ─────────────────────────────────────────────────────────────
CHROMA_DIR      = os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db')
EMBED_MODEL     = "all-MiniLM-L6-v2"
DOCS_COLLECTION = "nasa_documents"
QA_COLLECTION   = "nasa_qa_pairs"

# Confidence threshold — if Q&A similarity score is below this, fall back to docs
# ChromaDB cosine distance: 0.0 = perfect match, 2.0 = completely opposite
QA_CONFIDENCE_THRESHOLD = 0.35


def get_retriever():
    """Return both ChromaDB collections ready for querying."""
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    client   = PersistentClient(path=CHROMA_DIR)

    doc_collection = client.get_collection(DOCS_COLLECTION, embedding_function=embed_fn)
    qa_collection  = client.get_collection(QA_COLLECTION,  embedding_function=embed_fn)

    return doc_collection, qa_collection


def retrieve(query: str, doc_col, qa_col, n_results: int = 3) -> dict:
    """
    Hybrid retrieval:
    1. Search Q&A pairs first (fast, direct match)
    2. If confidence is low, fall back to document chunks
    3. Always also fetch doc chunks to enrich context

    Returns a dict with:
        - context        : str  — text to pass to the LLM
        - source         : str  — "qa" or "document"
        - matched_qa     : dict or None — the best Q&A match if used
        - doc_sources    : list — source URLs from document chunks
        - confidence     : float — similarity score of best Q&A match
    """

    # ── Stage 1: Search Q&A pairs ──────────────────────────────────────────────
    qa_results = qa_col.query(
        query_texts=[query],
        n_results=1,
        include=["documents", "metadatas", "distances"]
    )

    qa_distance   = qa_results["distances"][0][0]   if qa_results["distances"][0]   else 999
    qa_question   = qa_results["documents"][0][0]   if qa_results["documents"][0]   else ""
    qa_metadata   = qa_results["metadatas"][0][0]   if qa_results["metadatas"][0]   else {}
    qa_confidence = 1 - qa_distance                 # convert distance → similarity score

    # ── Stage 2: Always fetch document chunks for richer context ───────────────
    doc_results = doc_col.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    doc_chunks  = doc_results["documents"][0]  if doc_results["documents"][0]  else []
    doc_metas   = doc_results["metadatas"][0]  if doc_results["metadatas"][0]  else []
    doc_sources = list({m.get("source", "") for m in doc_metas if m.get("source")})

    # ── Stage 3: Decide which source to use ───────────────────────────────────
    use_qa = qa_distance < QA_CONFIDENCE_THRESHOLD and qa_metadata.get("answer")

    if use_qa:
        # High-confidence Q&A match — use the answer as primary context
        qa_answer = qa_metadata.get("answer", "")
        qa_source = qa_metadata.get("source_page", "")

        # Combine Q&A answer with supporting doc chunks for richer context
        context_parts = [
            f"[Best matching Q&A]\nQ: {qa_question}\nA: {qa_answer}",
        ]
        if doc_chunks:
            context_parts.append("\n[Supporting document excerpts]")
            context_parts.extend(doc_chunks[:2])   # add top 2 doc chunks

        context = "\n\n".join(context_parts)

        return {
            "context":     context,
            "source":      "qa",
            "matched_qa":  {
                "question": qa_question,
                "answer":   qa_answer,
                "source":   qa_source,
                "title":    qa_metadata.get("source_title", ""),
            },
            "doc_sources":  doc_sources,
            "confidence":   round(qa_confidence, 3),
        }

    else:
        # Low-confidence Q&A — fall back to raw document chunks
        context = "\n\n".join(doc_chunks) if doc_chunks else "No relevant content found."

        return {
            "context":    context,
            "source":     "document",
            "matched_qa": None,
            "doc_sources": doc_sources,
            "confidence":  round(qa_confidence, 3),
        }


if __name__ == "__main__":
    # Quick test
    print("🔍 Testing hybrid retriever...")
    doc_col, qa_col = get_retriever()

    test_queries = [
        "What is the Great Red Spot on Jupiter?",
        "How many moons does Saturn have?",
        "What is a black hole?",
    ]

    for q in test_queries:
        print(f"\nQ: {q}")
        result = retrieve(q, doc_col, qa_col)
        print(f"   Source     : {result['source']}")
        print(f"   Confidence : {result['confidence']}")
        print(f"   Context    : {result['context'][:120]}...")