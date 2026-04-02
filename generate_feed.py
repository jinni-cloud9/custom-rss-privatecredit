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
        'https://news.google.com/rss/search?q=site:reuters.com+('
        'merger+OR+acquisition+OR+buyout+OR+"take-private"+OR+"take+private"+'
        'OR+"leveraged+buyout"+OR+"private+equity+sponsor"+OR+"sponsored+buyout")+'
        '("UK"+OR+"Britain"+OR+"British"+OR+"England"+OR+"London"+OR+"Europe"+OR+"European"+'
        'OR+"EU"+OR+"Eurozone"+OR+"Germany"+OR+"France"+OR+"Italy"+OR+"Spain"+OR+"Netherlands"+'
        'OR+"Belgium"+OR+"Luxembourg"+OR+"Nordics"+OR+"Sweden"+OR+"Denmark"+OR+"Norway"+OR+"Finland"+'
        'OR+"Ireland"+OR+"Scotland"+OR+"Wales"+OR+"Poland"+OR+"Austria"+OR+"Switzerland")+'
        '-"United States"+-US+-"U.S."+'
        '&hl=en-GB&gl=GB&ceid=GB:en'
    ),
    (
        "Restructuring",
        'https://news.google.com/rss/search?q=site:reuters.com+('
        'restructuring+OR+bankruptcy+OR+"chapter+11"+OR+distressed+OR+"debt+exchange"+'
        'OR+"liability+management")+'
        '("UK"+OR+"Britain"+OR+"British"+OR+"England"+OR+"London"+OR+"Europe"+OR+"European"+'
        'OR+"EU"+OR+"Eurozone"+OR+"Germany"+OR+"France"+OR+"Italy"+OR+"Spain"+OR+"Netherlands"+'
        'OR+"Belgium"+OR+"Luxembourg"+OR+"Nordics"+OR+"Sweden"+OR+"Denmark"+OR+"Norway"+OR+"Finland"+'
        'OR+"Ireland"+OR+"Scotland"+OR+"Wales"+OR+"Poland"+OR+"Austria"+OR+"Switzerland")+'
        '-"United States"+-US+-"U.S."+'
        '&hl=en-GB&gl=GB&ceid=GB:en'
    ),
    (
        "Private Credit",
        'https://news.google.com/rss/search?q=site:reuters.com+('
        '"private+credit"+OR+"direct+lending"+OR+"private+debt"+OR+"private+lender"+'
        'OR+"non-bank+lender"+OR+"asset-backed+lending")+'
        '("UK"+OR+"Britain"+OR+"British"+OR+"England"+OR+"London"+OR+"Europe"+OR+"European"+'
        'OR+"EU"+OR+"Eurozone"+OR+"Germany"+OR+"France"+OR+"Italy"+OR+"Spain"+OR+"Netherlands"+'
        'OR+"Belgium"+OR+"Luxembourg"+OR+"Nordics"+OR+"Sweden"+OR+"Denmark"+OR+"Norway"+OR+"Finland"+'
        'OR+"Ireland"+OR+"Scotland"+OR+"Wales"+OR+"Poland"+OR+"Austria"+OR+"Switzerland")+'
        '-"United States"+-US+-"U.S."+'
        '&hl=en-GB&gl=GB&ceid=GB:en'
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

EUROPE_TERMS = [
    "uk", "britain", "british", "england", "london", "europe", "european",
    "eu", "eurozone", "germany", "france", "italy", "spain", "netherlands",
    "belgium", "luxembourg", "nordics", "sweden", "denmark", "norway",
    "finland", "ireland", "scotland", "wales", "poland", "austria",
    "switzerland"
]

US_TERMS = [
    "united states", "u.s.", " us ", "new york", "washington", "california",
    "texas", "florida", "delaware"
]





def fetch_xml(url):
    req = urllib.request.Request(
        url,[2:48 PM]headers={"User-Agent": "Mozilla/5.0"},
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

    return unquote(link).split("?")[0].rstrip("/")





def is_reuters_link(link, title, description, source):
    text = f"{link} {title} {description} {source}".lower()
    return "reuters.com" in text or "reuters" in text





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





def looks_us_only(title, description):
    text = f" {title} {description} ".lower()
    has_europe = any(term in text for term in EUROPE_TERMS)
    has_us = any(term in text for term in US_TERMS)
    return has_us and not has_europe





def extract_author(item):
    for tag in [
        "author",
        "{http://search.yahoo.com/mrss/}credit",
        "{http://purl.org/dc/elements/1.1/}creator",
    ]:
        node = item.find(tag)
        if node is not None and node.text:
            return normalize_whitespace(node.text)
    return ""





def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters Europe/UK: M&A, Restructuring, Private Credit")
    fg.link(href="https://news.google.com/")
    fg.description("Merged Reuters-focused feed for UK and pan-European M&A, restructuring, and private credit")
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
            source = normalize_whitespace(raw_source) if raw_source else "Reuters"

            if not link or not title:
                continue

            if not is_reuters_link(link, title, desc, source):
                continue

            if looks_us_only(title, desc):
                continue

            title_key = re.sub(r"[^a-z0-9]+", "", title.lower())

            if link in seen_links:
                continue

            if title_key in seen_title_keys:
                continue

            categories = classify_item(title, desc, default_category)

            source_bits = [source]
            if raw_author:
                source_bits.append(f"Author: {raw_author}")

            source_line = " | ".join(source_bits)
            tag_line = "Tags: " + ", ".join(categories)

            final_desc_parts = [tag_line, source_line]
            if desc:[2:48 PM]final_desc_parts.append(desc)

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
