from playwright.sync_api import sync_playwright

BLOCK_MARKERS = ("you have been blocked", "access denied", "verify you are human")
OPEN_MARKERS = ("book tickets", "book now")

def check_booking(url: str, debug: bool = False) -> dict:
    """Check if ticket booking is open on a movie page.

    Returns {"status": "open" | "not_open" | "blocked" | "error", "url": url}.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)  # let JavaScript content load
            text = page.inner_text("body").lower()
            if debug:
                page.screenshot(path="debug.png", full_page=True)
                with open("debug.txt", "w", encoding="utf-8") as f:
                    f.write(text)
            browser.close()
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}

    if any(m in text for m in BLOCK_MARKERS):
        status = "blocked"
    elif any(m in text for m in OPEN_MARKERS):
        status = "open"
    else:
        status = "not_open"
    return {"status": status, "url": url}

if __name__ == "__main__":
    import sys
    print(check_booking(sys.argv[1], debug="--debug" in sys.argv))