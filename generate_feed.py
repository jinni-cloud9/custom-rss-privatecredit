import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

FEEDS = [
    (
        "M&A",
        "https://news.google.com/rss/search?q=site:reuters.com+(merger+OR+acquisition+OR+buyout+OR+%22take-private%22+OR+%22take+private%22+OR+%22leveraged+buyout%22+OR+%22private+equity+sponsor%22+OR+%22sponsored+buyout%22)+(%22UK%22+OR+%22Britain%22+OR+%22British%22+OR+%22England%22+OR+%22London%22+OR+%22Europe%22+OR+%22European%22+OR+%22EU%22+OR+%22Eurozone%22+OR+%22Germany%22+OR+%22France%22+OR+%22Italy%22+OR+%22Spain%22+OR+%22Netherlands%22+OR+%22Belgium%22+OR+%22Luxembourg%22+OR+%22Nordics%22+OR+%22Sweden%22+OR+%22Denmark%22+OR+%22Norway%22+OR+%22Finland%22+OR+%22Ireland%22+OR+%22Scotland%22+OR+%22Wales%22+OR+%22Poland%22+OR+%22Austria%22+OR+%22Switzerland%22)+-%22United+States%22+-%22U.S.%22+-US&hl=en-GB&gl=GB&ceid=GB:en",
    ),
    (
        "Restructuring",
        "https://news.google.com/rss/search?q=site:reuters.com+(restructuring+OR+bankruptcy+OR+%22chapter+11%22+OR+distressed+OR+%22debt+exchange%22+OR+%22liability+management%22)+(%22UK%22+OR+%22Britain%22+OR+%22British%22+OR+%22England%22+OR+%22London%22+OR+%22Europe%22+OR+%22European%22+OR+%22EU%22+OR+%22Eurozone%22+OR+%22Germany%22+OR+%22France%22+OR+%22Italy%22+OR+%22Spain%22+OR+%22Netherlands%22+OR+%22Belgium%22+OR+%22Luxembourg%22+OR+%22Nordics%22+OR+%22Sweden%22+OR+%22Denmark%22+OR+%22Norway%22+OR+%22Finland%22+OR+%22Ireland%22+OR+%22Scotland%22+OR+%22Wales%22+OR+%22Poland%22+OR+%22Austria%22+OR+%22Switzerland%22)+-%22United+States%22+-%22U.S.%22+-US&hl=en-GB&gl=GB&ceid=GB:en",
    ),
    (
        "Private Credit",
        "https://news.google.com/rss/search?q=site:reuters.com+(%22private+credit%22+OR+%22direct+lending%22+OR+%22private+debt%22+OR+%22private+lender%22+OR+%22non-bank+lender%22+OR+%22asset-backed+lending%22)+(%22UK%22+OR+%22Britain%22+OR+%22British%22+OR+%22England%22+OR+%22London%22+OR+%22Europe%22+OR+%22European%22+OR+%22EU%22+OR+%22Eurozone%22+OR+%22Germany%22+OR+%22France%22+OR+%22Italy%22+OR+%22Spain%22+OR+%22Netherlands%22+OR+%22Belgium%22+OR+%22Luxembourg%22+OR+%22Nordics%22+OR+%22Sweden%22+OR+%22Denmark%22+OR+%22Norway%22+OR+%22Finland%22+OR+%22Ireland%22+OR+%22Scotland%22+OR+%22Wales%22+OR+%22Poland%22+OR+%22Austria%22+OR+%22Switzerland%22)+-%22United+States%22+-%22U.S.%22+-US&hl=en-GB&gl=GB&ceid=GB:en",
    ),
]

def fetch_xml(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def get_child_text(node, name):
    child = node.find(name)
    if child is not None and child.text:
        return child.text.strip()
    return ""

def clean_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters Europe/UK: Private Credit")
    fg.link(href="https://news.google.com/")
    fg.description("Reuters Europe/UK feed for M&A, restructuring, and private credit")
    fg.language("en")

    seen_titles = set()
    total = 0

    for tag, url in FEEDS:
        xml_bytes = fetch_xml(url)
        root = ET.fromstring(xml_bytes)
        channel = root.find("channel")
        if channel is None:
            continue

        for item in channel.findall("item"):
            title = clean_text(get_child_text(item, "title"))
            link = clean_text(get_child_text(item, "link"))
            pub_date = clean_text(get_child_text(item, "pubDate"))[2:54 PM]source = clean_text(get_child_text(item, "source"))
            author = clean_text(get_child_text(item, "author"))

            if not title or not link:
                continue

            title_key = title.lower()
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)

            subhead_parts = [tag]
            if source:
                subhead_parts.append(source)
            else:
                subhead_parts.append("Reuters")
            if author:
                subhead_parts.append(author)

            subhead = " | ".join(subhead_parts)

            entry = fg.add_entry()
            entry.id(link)
            entry.title(title)
            entry.link(href=link)
            entry.description(subhead)

            if pub_date:
                entry.pubDate(pub_date)

            total += 1

    print("Total merged items:", total)
    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print("Wrote", OUTPUT_FILE)
