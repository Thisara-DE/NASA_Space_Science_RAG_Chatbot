import requests
from bs4 import BeautifulSoup
import os
import time
import json

# ── Output folder ──────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

# ── Pages to scrape ────────────────────────────────────────────────────────────
URLS = [
    "https://science.nasa.gov/solar-system/",
    "https://science.nasa.gov/solar-system/planets/",
    "https://science.nasa.gov/solar-system/planets/mercury/",
    "https://science.nasa.gov/solar-system/planets/venus/",
    "https://science.nasa.gov/solar-system/planets/earth/",
    "https://science.nasa.gov/solar-system/planets/mars/",
    "https://science.nasa.gov/solar-system/planets/jupiter/",
    "https://science.nasa.gov/solar-system/planets/saturn/",
    "https://science.nasa.gov/solar-system/planets/uranus/",
    "https://science.nasa.gov/solar-system/planets/neptune/",
    "https://science.nasa.gov/solar-system/the-sun/",
    "https://science.nasa.gov/solar-system/moons/",
    "https://science.nasa.gov/solar-system/asteroids/",
    "https://science.nasa.gov/solar-system/comets/",
    "https://science.nasa.gov/universe/",
    "https://science.nasa.gov/astrophysics/",
    "https://science.nasa.gov/earth/",
    "https://science.nasa.gov/planetary-science/",
    "https://science.nasa.gov/heliophysics/",
    "https://science.nasa.gov/solar-system/beyond-our-solar-system/",
]

# ── Headers so NASA doesn't block us ──────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def clean_text(soup: BeautifulSoup) -> str:
    """Remove nav, footer, scripts, styles and return clean plain text."""
    for tag in soup(["nav", "footer", "header", "script", "style",
                    "aside", "form", "noscript", "iframe"]):
        tag.decompose()

    # Try to grab the main content area first
    main = soup.find("main") or soup.find("article") or soup.find("body")
    text = main.get_text(separator="\n") if main else soup.get_text(separator="\n")

    # Clean up excessive whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if len(line) > 40]   # drop short nav fragments
    return "\n".join(lines)


def scrape_page(url: str) -> dict | None:
    """Fetch one URL and return a dict with url + cleaned text, or None on error."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Page title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        text = clean_text(soup)

        if len(text) < 200:
            print(f"  ⚠ Too little content on {url} — skipping")
            return None

        return {"url": url, "title": title, "text": text}

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to fetch {url}: {e}")
        return None


def save_page(page: dict, index: int) -> None:
    """Save a scraped page as a .txt file in data/raw/."""
    # Build a safe filename from the URL path
    slug = page["url"].rstrip("/").split("/")[-1] or f"page_{index}"
    slug = slug.replace("-", "_")[:50]
    filename = f"{index:02d}_{slug}.txt"
    filepath = os.path.join(RAW_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"URL: {page['url']}\n")
        f.write(f"TITLE: {page['title']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(page["text"])

    print(f"  ✓ Saved → {filename}  ({len(page['text'])} chars)")


def save_metadata(pages: list[dict]) -> None:
    """Save a JSON index of all scraped pages for later use."""
    meta_path = os.path.join(RAW_DIR, "_metadata.json")
    metadata = [{"index": i, "url": p["url"], "title": p["title"],
                "char_count": len(p["text"])} for i, p in enumerate(pages)]
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n📋 Metadata saved → {meta_path}")


def main():
    print("🚀 NASA Space Science Scraper")
    print(f"   Target: {len(URLS)} pages from science.nasa.gov")
    print("=" * 50)

    scraped = []

    for i, url in enumerate(URLS):
        print(f"\n[{i+1}/{len(URLS)}] {url}")
        page = scrape_page(url)
        if page:
            save_page(page, i)
            scraped.append(page)
        time.sleep(1.5)   # be polite — don't hammer NASA's servers

    save_metadata(scraped)

    print("\n" + "=" * 50)
    print(f"✅ Done! Scraped {len(scraped)}/{len(URLS)} pages successfully.")
    print(f"   Files saved in: data/raw/")


if __name__ == "__main__":
    main()