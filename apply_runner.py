
import asyncio, json, random
from pathlib import Path
from playwright.async_api import async_playwright
from models import SessionLocal, Job, Application

PROFILE = json.loads(Path("data/static_profile.json").read_text())

async def prefill(page):
    # Best-effort prefill for common ATS fields
    # Name
    for sel in ['input[name="name"]','input[name="fullName"]','input[aria-label="Full name"]']:
        el = await page.query_selector(sel)
        if el: await el.fill(PROFILE["full_name"]); break
    # Email
    for sel in ['input[type="email"]','input[name="email"]']:
        el = await page.query_selector(sel)
        if el: await el.fill(PROFILE["email"]); break
    # Phone
    for sel in ['input[type="tel"]','input[name="phone"]','input[autocomplete="tel"]']:
        el = await page.query_selector(sel)
        if el: await el.fill(PROFILE["phone"]); break
    # Resume upload
    for sel in ['input[type="file"]','input[name="resume"]','input[accept*="pdf"]']:
        el = await page.query_selector(sel)
        if el:
            try:
                await el.set_input_files(PROFILE["resume_path"])
            except Exception:
                pass
            break

async def run_apply():
    db = SessionLocal()
    jobs = db.query(Job).filter(Job.status=="new").limit(5).all()
    if not jobs:
        print("No new jobs.")
        return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # show UI for manual submit
        ctx = await browser.new_context()
        page = await ctx.new_page()
        for j in jobs:
            print("Opening:", j.company, "-", j.title)
            await page.goto(j.link)
            await page.wait_for_load_state("domcontentloaded")

            # Prefer company site
            clicked = False
            for sel in ['a:has-text("Apply on company site")','a:has-text("Apply on company website")','a:has-text("Apply on company")']:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    clicked = True
                    break
            if not clicked:
                # fall back to Easy Apply flow (keep manual final submit)
                for sel in ['button:has-text("Easy Apply")','button:has-text("Apply")']:
                    el = await page.query_selector(sel)
                    if el:
                        await el.click()
                        break

            await page.wait_for_load_state("domcontentloaded")
            try:
                await prefill(page)
            except Exception:
                pass

            app = Application(job_id=j.id, submitted=False)
            db.add(app)
            j.status = "applied"
            db.commit()

            # Pause for review & manual submit
            await page.wait_for_timeout(random.randint(12000, 20000))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_apply())
