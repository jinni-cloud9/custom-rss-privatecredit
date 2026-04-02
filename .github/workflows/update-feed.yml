import urllib.request
import xml.etree.ElementTree as ET
from feedgen.feed import FeedGenerator

FEEDS = [
    {
        "title": "Reuters Europe/UK Sponsor-Backed M&A",
        "description": "Reuters Europe/UK sponsor-backed M&A feed",
        "output": "sponsor-backed-ma.xml",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+((%22take-private%22+OR+%22take+private%22+OR+buyout+OR+%22leveraged+buyout%22+OR+LBO+OR+%22private+equity%22+OR+%22private+equity+sponsor%22+OR+%22sponsor-backed%22+OR+%22sponsored+buyout%22)+(%22UK%22+OR+%22Britain%22+OR+%22British%22+OR+%22London%22+OR+%22Europe%22+OR+%22European%22+OR+%22Western+Europe%22+OR+%22EU%22+OR+%22Eurozone%22+OR+%22Germany%22+OR+%22France%22+OR+%22Italy%22+OR+%22Spain%22+OR+%22Netherlands%22+OR+%22Belgium%22+OR+%22Luxembourg%22+OR+%22Sweden%22+OR+%22Denmark%22+OR+%22Norway%22+OR+%22Finland%22+OR+%22Ireland%22+OR+%22Austria%22+OR+%22Switzerland%22)+-%22United+States%22+-%22U.S.%22+-US+-%22New+York%22+-%22Nasdaq%22+-%22NYSE%22+-%22agreed+merger%22+-%22shares+jump+on+bid%22+-%22all-stock+merger%22+-%22public+company+merger%22+-%22merger+of+equals%22)&hl=en-GB&gl=GB&ceid=GB:en",
    },
    {
        "title": "Europe/UK Restructuring",
        "description": "Europe/UK restructuring feed",
        "output": "restructuring.xml",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+((restructuring+OR+distressed+OR+%22debt+exchange%22+OR+%22liability+management%22+OR+recapitalisation+OR+recapitalization+OR+insolvency)+(%22UK%22+OR+%22Britain%22+OR+%22British%22+OR+%22London%22+OR+%22Europe%22+OR+%22European%22+OR+%22Western+Europe%22+OR+%22EU%22+OR+%22Eurozone%22+OR+%22Germany%22+OR+%22France%22+OR+%22Italy%22+OR+%22Spain%22+OR+%22Netherlands%22+OR+%22Belgium%22+OR+%22Luxembourg%22+OR+%22Sweden%22+OR+%22Denmark%22+OR+%22Norway%22+OR+%22Finland%22+OR+%22Ireland%22+OR+%22Austria%22+OR+%22Switzerland%22)+-%22United+States%22+-%22U.S.%22+-US+-%22New+York%22+-%22Chapter+11%22)&hl=en-GB&gl=GB&ceid=GB:en",
    },
    {
        "title": "Europe/UK Private Credit",
        "description": "Europe/UK private credit feed",
        "output": "private-credit.xml",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+((%22private+credit%22+OR+%22direct+lending%22+OR+%22private+debt%22+OR+%22private+lender%22+OR+%22non-bank+lender%22+OR+%22asset-backed+lending%22+OR+unitranche)+(%22UK%22+OR+%22Britain%22+OR+%22British%22+OR+%22London%22+OR+%22Europe%22+OR+%22European%22+OR+%22Western+Europe%22+OR+%22EU%22+OR+%22Eurozone%22+OR+%22Germany%22+OR+%22France%22+OR+%22Italy%22+OR+%22Spain%22+OR+%22Netherlands%22+OR+%22Belgium%22+OR+%22Luxembourg%22+OR+%22Sweden%22+OR+%22Denmark%22+OR+%22Norway%22+OR+%22Finland%22+OR+%22Ireland%22+OR+%22Austria%22+OR+%22Switzerland%22)+-%22United+States%22+-%22U.S.%22+-US+-%22New+York%22)&hl=en-GB&gl=GB&ceid=GB:en",
    },
]

def fetch_xml(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def get_text(node, tag_name):
    child = node.find(tag_name)
    if child is not None and child.text:
        return child.text.strip()
    return ""

def write_feed(feed_config):
    data = fetch_xml(feed_config["url"])
    root = ET.fromstring(data)
    channel = root.find("channel")
    if channel is None:
        return

    fg = FeedGenerator()
    fg.title(feed_config["title"])
    fg.link(href="https://news.google.com/")
    fg.description(feed_config["description"])
    fg.language("en")

    seen = set()

    for item in channel.findall("item"):
        title = get_text(item, "title") or "Untitled"[3:22 PM]link = get_text(item, "link")
        desc = get_text(item, "description")
        pub = get_text(item, "pubDate")

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

    fg.rss_file(feed_config["output"])
    print("Wrote", feed_config["output"])

def main():
    for feed in FEEDS:
        write_feed(feed)

if name == "main":
    main()
