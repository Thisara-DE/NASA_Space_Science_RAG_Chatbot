import os
import json
import time
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# ── Load environment variables (.env file) ─────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Paths ──────────────────────────────────────────────────────────────────────
RAW_DIR       = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
OUTPUT_CSV    = os.path.join(os.path.dirname(__file__), '..', 'data', 'qa_dataset.csv')
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ── Groq client ────────────────────────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"   # free, fast, good quality

# ── How many Q&A pairs to request per page ─────────────────────────────────────
QA_PER_PAGE = 8


def read_raw_files() -> list[dict]:
    """Read all .txt files from data/raw/ (skip the metadata JSON)."""
    pages = []
    for filename in sorted(os.listdir(RAW_DIR)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(RAW_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse out the URL and title from the header we wrote in scraper.py
        lines   = content.splitlines()
        url     = lines[0].replace("URL: ", "").strip()   if lines else ""
        title   = lines[1].replace("TITLE: ", "").strip() if len(lines) > 1 else filename
        # The actual text starts after the === divider (line 3 onwards)
        text    = "\n".join(lines[3:]).strip()

        pages.append({"filename": filename, "url": url, "title": title, "text": text})
    return pages


def chunk_text(text: str, max_chars: int = 3000) -> str:
    """Trim text to max_chars so we don't exceed the LLM context window."""
    return text[:max_chars] if len(text) > max_chars else text


def build_prompt(text: str, num_pairs: int) -> str:
    """Build the prompt that asks the LLM to generate Q&A pairs."""
    return f"""You are an expert NASA science educator. Based ONLY on the content below, generate exactly {num_pairs} high-quality question and answer pairs.

Rules:
- Questions must be specific and answerable from the content
- Answers must be detailed (2-4 sentences), accurate, and written in plain English
- Do NOT make up information not present in the content
- Cover different aspects of the content (don't repeat similar questions)
- Return ONLY valid JSON — no extra text, no markdown, no code blocks

Return this exact JSON format:
[
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
]

CONTENT:
{text}
"""


def generate_qa_pairs(page: dict) -> list[dict]:
    """Call Groq API to generate Q&A pairs for one page."""
    text   = chunk_text(page["text"])
    prompt = build_prompt(text, QA_PER_PAGE)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,    # lower = more factual, less creative
            max_tokens=2048,
        )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Model returned no text content")
        raw = content.strip()

        # Strip markdown code fences if the model added them anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        pairs = json.loads(raw)

        # Attach source info to every pair
        result = []
        for pair in pairs:
            if "question" in pair and "answer" in pair:
                result.append({
                    "question":    pair["question"].strip(),
                    "answer":      pair["answer"].strip(),
                    "source_page": page["url"],
                    "source_title": page["title"],
                })
        return result

    except json.JSONDecodeError as e:
        print(f"    ⚠ JSON parse error for {page['filename']}: {e}")
        return []
    except Exception as e:
        print(f"    ✗ API error for {page['filename']}: {e}")
        return []


def save_processed_text(page: dict) -> None:
    """Save a cleaned copy of the page text to data/processed/."""
    out_path = os.path.join(PROCESSED_DIR, page["filename"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"URL: {page['url']}\n")
        f.write(f"TITLE: {page['title']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(page["text"])


def main():
    print("🤖 NASA Q&A Generator (powered by Groq)")
    print(f"   Model : {MODEL}")
    print(f"   Target: {QA_PER_PAGE} Q&A pairs per page")
    print("=" * 50)

    pages = read_raw_files()
    if not pages:
        print("❌ No .txt files found in data/raw/ — run scraper.py first!")
        return

    print(f"📄 Found {len(pages)} scraped pages\n")

    all_pairs = []

    for i, page in enumerate(pages):
        print(f"[{i+1}/{len(pages)}] {page['title'][:60]}")
        pairs = generate_qa_pairs(page)

        if pairs:
            all_pairs.extend(pairs)
            print(f"    ✓ Generated {len(pairs)} Q&A pairs")
        else:
            print(f"    ⚠ No pairs generated — skipping")

        save_processed_text(page)
        time.sleep(1)   # stay within Groq free-tier rate limits

    # ── Save to CSV ────────────────────────────────────────────────────────────
    if all_pairs:
        df = pd.DataFrame(all_pairs)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

        print("\n" + "=" * 50)
        print(f"✅ Done! Generated {len(all_pairs)} Q&A pairs total")
        print(f"   Saved → data/qa_dataset.csv")
        print(f"\n📊 Sample Q&A pairs:")
        print("-" * 50)
        for row in all_pairs[:3]:
            print(f"Q: {row['question']}")
            print(f"A: {row['answer'][:120]}...")
            print()
    else:
        print("❌ No Q&A pairs generated. Check your GROQ_API_KEY in .env")


if __name__ == "__main__":
    main()