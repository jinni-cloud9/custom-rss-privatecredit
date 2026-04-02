from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator

OUTPUT_FILE = "reuters_filtered.xml"

def build_feed():
    fg = FeedGenerator()
    fg.title("Reuters link debug")
    fg.link(href="https://www.reuters.com/")
    fg.description("Reuters link debug")
    fg.language("en")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.reuters.com/business/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        links = page.locator("a").evaluate_all(
            """els => els.map(a => a.href).filter(Boolean)"""
        )

        print(f"Total raw links found: {len(links)}")
        for href in links[:20]:
            print(href)

        count = 0
        seen = set()

        for href in links:
            href = href.split("?")[0]
            if not href.startswith("https://www.reuters.com/"):
                continue
            if href in seen:
                continue
            seen.add(href)

            fe = fg.add_entry()
            fe.id(href)
            fe.title(href)
            fe.link(href=href)
            fe.description("Discovered Reuters link")
            count += 1

            if count >= 10:
                break

        print(f"Filtered Reuters links added: {count}")
        browser.close()

    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    build_feed()
    print("Wrote reuters_filtered.xml")
