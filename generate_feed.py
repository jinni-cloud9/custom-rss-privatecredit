import urllib.request
import xml.etree.ElementTree as ET
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

FEEDS = [
    "https://news.google.com/rss/search?q=site:reuters.com+(merger+OR+acquisition+OR+buyout+OR+%22take-private%22+OR+%22take+private%22)&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=site:reuters.com+(restructuring+OR+bankruptcy+OR+%22chapter+11%22+OR+distressed+OR+%22debt+exchange%22+OR+%22liability+management%22)&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=site:reuters.com+(%22private+credit%22+OR+%22direct+lending%22+OR+%22private+debt%22+OR+%22private+lender%22+OR+%22non-bank+lender%22)&hl=en-US&gl=US&ceid=US:en",
]

def fetch_xml(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters: M&A, Restructuring, Private Credit")
    fg.link(href="https://news.google.com/")
    fg.description("Merged Google News RSS feeds filtered to Reuters for M&A, restructuring, and private credit")
    fg.language("en")

    seen = set()
    total = 0

    for feed_url in FEEDS:
        data = fetch_xml(feed_url)
        root = ET.fromstring(data)

        channel = root.find("channel")
        if channel is None:
            continue

        for item in channel.findall("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")

            title = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"
            link = link_el.text.strip() if link_el is not None and link_el.text else None
            desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
            pub = pub_el.text.strip() if pub_el is not None and pub_el.text else None

            if not link or link in seen:
                continue

            seen.add(link)

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.description(desc or title)
            if pub:
                fe.pubDate(pub)

            total += 1

    print(f"Total merged items: {total}")
    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print(f"Wrote {OUTPUT_FILE}")
