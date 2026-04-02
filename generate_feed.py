import re
import html
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs, unquote
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

FEEDS = [
    (
        "M&A",
        "https://news.google.com/rss/search?q=site:reuters.com+(merger+OR+acquisition+OR+buyout+OR+%22take-private%22+OR+%22take+private%22+OR+%22leveraged+buyout%22+OR+%22private+equity+sponsor%22+OR+%22sponsored+buyout%22)&hl=en-US&gl=US&ceid=US:en",
    ),
    (
        "Restructuring",
        "https://news.google.com/rss/search?q=site:reuters.com+(restructuring+OR+bankruptcy+OR+%22chapter+11%22+OR+distressed+OR+%22debt+exchange%22+OR+%22liability+management%22)&hl=en-US&gl=US&ceid=US:en",
    ),
    (
        "Private Credit",
        "https://news.google.com/rss/search?q=site:reuters.com+(%22private+credit%22+OR+%22direct+lending%22+OR+%22private+debt%22+OR+%22private+lender%22+OR+%22non-bank+lender%22+OR+%22asset-backed+lending%22)&hl=en-US&gl=US&ceid=US:en",
    ),
]

CATEGORY_KEYWORDS = {
    "M&A": [
        "merger",
        "acquisition",
        "buyout",
        "take-private",
        "take private",
        "leveraged buyout",
        "private equity sponsor",
        "sponsored buyout",
    ],
    "Restructuring": [
        "restructuring",
        "bankruptcy",
        "chapter 11",
        "distressed",
        "debt exchange",
        "liability management",
    ],
    "Private Credit": [
        "private credit",
        "direct lending",
        "private debt",
        "private lender",
        "non-bank lender",
        "asset-backed lending",
    ],
}





def fetch_xml(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()





def get_text(element, tag_name):
    child = element.find(tag_name)
    if child is not None and child.text:
        return child.text.strip()
    return ""





def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text or "").strip()





def normalize_title(title):
    title = html.unescape(title or "")
    title = normalize_whitespace(title)
    title = re.sub(r"\s*[-|]\s*Reuters\s*$", "", title, flags=re.IGNORECASE)
    return title.strip()





def canonicalize_link(link):
    if not link:
        return ""

    parsed = urlparse(link)

    if "news.google.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "url" in qs and qs["url"]:
            return qs["url"][0].split("?")[0].rstrip("/")

    clean = unquote(link).split("?")[0].rstrip("/")
    return clean





def is_reuters_link(link, title, description):
    text = f"{link} {title} {description}".lower()
    return "reuters.com" in text or " - reuters" in text or title.lower().endswith("reuters")





def classify_item(title, description, default_category):
    text = f"{title} {description}".lower()
    matched = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                matched.append(category)
                break

    if not matched:
        matched = [default_category]

    return matched





def extract_author(item):
    for tag in ["author", "{http://search.yahoo.com/mrss/}credit", "{http://purl.org/dc/elements/1.1/}creator"]:
        node = item.find(tag)[2:45 PM]if node is not None and node.text:
            return normalize_whitespace(node.text)
    return ""





def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters: M&A, Restructuring, Private Credit")
    fg.link(href="https://news.google.com/")
    fg.description("Merged Reuters-focused feed for M&A, restructuring, and private credit")
    fg.language("en")

    seen_links = set()
    seen_title_keys = set()
    total = 0

    for default_category, feed_url in FEEDS:
        data = fetch_xml(feed_url)
        root = ET.fromstring(data)

        channel = root.find("channel")
        if channel is None:
            continue

        for item in channel.findall("item"):
            raw_title = get_text(item, "title")
            raw_link = get_text(item, "link")
            raw_desc = get_text(item, "description")
            raw_pub = get_text(item, "pubDate")
            raw_source = get_text(item, "source")
            raw_author = extract_author(item)

            title = normalize_title(raw_title)
            link = canonicalize_link(raw_link)
            desc = normalize_whitespace(html.unescape(raw_desc))

            if not link or not title:
                continue

            if not is_reuters_link(link, title, desc):
                continue

            title_key = re.sub(r"[^a-z0-9]+", "", title.lower())

            if link in seen_links:
                continue

            if title_key in seen_title_keys:
                continue

            categories = classify_item(title, desc, default_category)

            source_bits = []
            if raw_source:
                source_bits.append(normalize_whitespace(raw_source))
            else:
                source_bits.append("Reuters")

            if raw_author:
                source_bits.append(f"Author: {raw_author}")

            source_line = " | ".join(source_bits)
            tag_line = "Tags: " + ", ".join(categories)

            final_desc_parts = [tag_line, source_line]
            if desc:
                final_desc_parts.append(desc)

            final_desc = "<br/>".join(final_desc_parts)

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.description(final_desc)

            for category in categories:
                fe.category(term=category)

            if raw_author:
                fe.author({"name": raw_author})

            if raw_pub:
                fe.pubDate(raw_pub)

            seen_links.add(link)
            seen_title_keys.add(title_key)
            total += 1

    print(f"Total merged items: {total}")
    fg.rss_file(OUTPUT_FILE)





if __name__ == "__main__":
    build_feed()
    print(f"Wrote {OUTPUT_FILE}")
Also simplify `requirements.txt` to:

```text
feedgen==1.0.0




And keep your workflow as the simpler non-Playwright one:

yaml
name: Update Reuters RSS Feed

on:
  workflow_dispatch:
  schedule:
    - cron: "*/30 * * * *"

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate RSS feed
        run: python generate_feed.py

      - name: Verify RSS file exists
        run: |
          ls -l
          test -f reuters_filtered.xml

      - name: Commit and push if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add reuters_filtered.xml
          git diff --staged --quiet || git commit -m "Update Reuters RSS feed"
          git push
