
import asyncio, os, random
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from models import SessionLocal, Job, init_db

SEARCH = {
    "keywords": "Senior Backend Engineer Go AWS (H1B OR visa OR sponsorship)",
    "location": "United States",
    "f_TPR": "r604800",  # last 7d (r86400 for 24h)
    "f_WT": "2,3",      # hybrid=2, remote=3
}

def search_url():
    base = "https://www.linkedin.com/jobs/search/?"
    q = {
        "keywords": SEARCH["keywords"],
        "location": SEARCH["location"],
        "f_TPR": SEARCH["f_TPR"],
        "f_WT": SEARCH["f_WT"],
        "refresh": "true"
    }
    return base + urlencode(q, safe="(),")

async def scrape():
    init_db()
    db = SessionLocal()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()

        # Login
        await page.goto("https://www.linkedin.com/login")
        await page.fill("#username", os.environ.get("LINKEDIN_EMAIL", ""))
        await page.fill("#password", os.environ.get("LINKEDIN_PASS", ""))
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        url = search_url()
        await page.goto(url)
        await page.wait_for_selector(".jobs-search__results-list li", timeout=30000)

        # Scroll to load more
        for _ in range(6):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(random.randint(900, 1500))

        html = await page.content()
        soup = BeautifulSoup(html, "html5lib")

        count = 0
        for li in soup.select(".jobs-search__results-list li"):
            title_el = li.select_one("a.job-card-container__link")
            company_el = li.select_one(".job-card-container__primary-description")
            location_el = li.select_one(".job-card-container__metadata-item")
            link = title_el["href"] if title_el and title_el.has_attr("href") else None
            title = title_el.get_text(strip=True) if title_el else None
            company = company_el.get_text(strip=True) if company_el else None
            location = location_el.get_text(strip=True) if location_el else ""

            if not (title and company and link):
                continue

            platform_id = None
            if "currentJobId=" in link:
                platform_id = link.split("currentJobId=")[-1].split("&")[0]
            elif "/view/" in link:
                platform_id = link.split("/view/")[1].split("/")[0]

            job = Job(platform_id=platform_id or link, title=title, company=company, link=link, source="linkedin", location=location)
            try:
                db.add(job)
                db.commit()
                count += 1
            except Exception:
                db.rollback()  # likely duplicate
        await browser.close()
    print(f"Scrape done. Added {count} jobs.")

if __name__ == "__main__":
    asyncio.run(scrape())
