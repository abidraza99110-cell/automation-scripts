import asyncio
import pandas as pd
import random
from playwright.async_api import async_playwright

# ---------------------------
# 1. SCRAPE DATA
# ---------------------------
async def scrape_data():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        page = await context.new_page()

        current_url = "https://news.ycombinator.com/"

        for _ in range(3):  # scrape 3 pages
            await page.goto(current_url, wait_until="networkidle")

            # Anti-bot delay
            await asyncio.sleep(random.uniform(1, 3))

            articles = await page.query_selector_all("tr.athing")

            for article in articles:
                rank = await article.query_selector(".rank")
                rank = int((await rank.inner_text()).replace(".", "")) if rank else None

                title_el = await article.query_selector(".titleline a")
                title = await title_el.inner_text() if title_el else None
                post_url = await title_el.get_attribute("href") if title_el else None

                subtext = await article.evaluate_handle(
                    "(el) => el.nextElementSibling"
                )

                # Points
                points = 0
                score_el = await subtext.query_selector(".score")
                if score_el:
                    points_text = await score_el.inner_text()
                    points = int(points_text.split()[0])

                # Author
                author = None
                author_el = await subtext.query_selector(".hnuser")
                if author_el:
                    author = await author_el.inner_text()

                # Comments
                comments = 0
                comment_links = await subtext.query_selector_all("a")
                for link in comment_links:
                    text = await link.inner_text()
                    if "comment" in text:
                        if text == "discuss":
                            comments = 0
                        else:
                            comments = int(text.split()[0])

                results.append({
                    "Rank": rank,
                    "Title": title,
                    "Author": author,
                    "Points": points,
                    "Comments": comments,
                    "URL": post_url
                })

            # Move to next page using "More" link
            more_btn = await page.query_selector("a.morelink")
            if more_btn:
                current_url = await more_btn.get_attribute("href")
                current_url = "https://news.ycombinator.com/" + current_url
            else:
                break

        await browser.close()

    return results


# ---------------------------
# 2. PROCESS DATA
# ---------------------------
def process_data(data):
    processed = []

    for item in data:
        if item["Points"] >= 100:
            category = "Trending"
        elif item["Comments"] >= 50:
            category = "Hot Discussion"
        else:
            category = "Normal"

        processed.append({
            "Rank": item["Rank"],
            "Title": item["Title"],
            "Author": item["Author"],
            "Points": item["Points"],
            "Comments": item["Comments"],
            "Category": category,
            "URL": item["URL"]
        })

    # Sort by Points descending
    processed.sort(key=lambda x: x["Points"], reverse=True)

    return processed


# ---------------------------
# 3. EXPORT DATA
# ---------------------------
def export_data(data):
    df = pd.DataFrame(data)
    df.to_csv("hn_analysis.csv", index=False)
    print(df.head())
    print("✅ Data exported successfully as hn_analysis.csv")


# ---------------------------
# MAIN EXECUTION
# ---------------------------
async def main():
    raw_data = await scrape_data()
    final_data = process_data(raw_data)
    export_data(final_data)

asyncio.run(main())
