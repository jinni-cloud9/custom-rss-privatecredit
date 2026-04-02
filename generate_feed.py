import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

FEEDS = [
    (
        "M&A",
        "https://news.google.com/rss/search?q=site:reuters.com+(merger+OR+acquisition+OR+buyout+OR+%22take-private%22+OR+%22take+private%22)&hl=en-US&gl=US&ceid=US:en",
    ),
    (
        "Restructuring",
        "https://news.google.com/rss/search?q=site:reuters.com+(restructuring+OR+bankruptcy+OR+%22chapter+11%22+OR+distressed+OR+%22debt+exchange%22+OR+%22liability+management%22)&hl=en-US&gl=US&ceid=US:en",
    ),
    (
        "Private Credit",
        "https://news.google.com/rss/search?q=site:reuters.com+(%22private+credit%22+OR+%22direct+lending%22+OR+%22private+debt%22+OR+%22private+lender%22+OR+%22non-bank+lender%22)&hl=en-US&gl=US&ceid=US:en",
    ),
]

def fetch_xml(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def get_text(item, tag_name):
    node = item.find(tag_name)
    if node is not None and node.text:
        return node.text.strip()
    return ""

def clean_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_author(item):
    author = get_text(item, "author")
    if author:
        return clean_text(author)

    dc_creator = item.find("{http://purl.org/dc/elements/1.1/}creator")
    if dc_creator is not None and dc_creator.text:
        return clean_text(dc_creator.text)

    media_credit = item.find("{http://search.yahoo.com/mrss/}credit")
    if media_credit is not None and media_credit.text:
        return clean_text(media_credit.text)

    return ""

def get_subhead(item, topic, author):
    desc = clean_text(get_text(item, "description"))

    if desc:
        parts = [p.strip() for p in desc.split(" - ") if p.strip()]
        if len(parts) >= 2:
            source_part = parts[-1]
            summary_part = " - ".join(parts[:-1]).strip()
            if summary_part and summary_part.lower() != "reuters":
                if author:
                    return f"{topic} | {author} | {summary_part}"
                return f"{topic} | {summary_part}"

    if author:
        return f"{topic} | {author}"

    return topic

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters: M&A, Restructuring, Private Credit")
    fg.link(href="https://news.google.com/")
    fg.description("Merged Google News RSS feeds filtered to Reuters for M&A, restructuring, and private credit")
    fg.language("en")

    seen = set()
    total = 0

    for topic, feed_url in FEEDS:
        data = fetch_xml(feed_url)
        root = ET.fromstring(data)

        channel = root.find("channel")
        if channel is None:
            continue

        for item in channel.findall("item"):
            title = clean_text(get_text(item, "title")) or "Untitled"
            link = clean_text(get_text(item, "link"))
            pub_date = clean_text(get_text(item, "pubDate"))
            author = get_author(item)
            subhead = get_subhead(item, topic, author)

            if not link or link in seen:
                continue

            seen.add(link)

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.description(subhead)

            if pub_date:
                fe.pubDate(pub_date)

            total += 1

    print(f"Total merged items: {total}")
    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print(f"Wrote {OUTPUT_FILE}")
