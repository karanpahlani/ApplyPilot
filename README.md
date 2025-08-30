
# applypilot

A pragmatic, hybrid automation to **scrape roles from LinkedIn, prefill/apply on ATS pages with human review**, send **personalized cold emails**, and **watch for confirmation emails**.

> ⚠️ Use responsibly. Many job sites prohibit full automation. This tool keeps the final submit manual by default.

---

## Features
- Playwright scraper for LinkedIn job search results
- Semi-auto apply runner: opens role pages, prefers "Apply on company site", prefills common fields, **you** hit Submit
- Cold recruiter emails via Gmail API + Jinja template
- IMAP watcher to capture "application received" confirmations
- SQLite tracking of jobs and applications

## Quickstart

### 1) Python & deps
```bash
python -V           # 3.10+ recommended
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

### 2) Configure environment
Copy `.env.example` → `.env` and fill values.

Add your resume at `data/karan_resume.pdf` and update `data/static_profile.json` as needed.

### 3) Initialize DB
```bash
python -c "from models import init_db; init_db(); print('DB ready')"
```

### 4) Scrape LinkedIn
```bash
python main.py scrape
```
- Logs into LinkedIn (email/password) and saves new roles to `app.db`.
- Adjust search keywords and filters in `scrape_linkedin.py#SEARCH`.

### 5) Apply (semi-automatic)
```bash
python main.py apply
```
- Opens each new job (headful browser), prefers "Apply on company site", attempts to prefill.
- **You review and click Submit** to keep things safe and accurate.
- Status is updated in DB.

### 6) Watch confirmation emails
Use Gmail **App Password** or OAuth. With IMAP + app password:
```bash
python main.py watch
```
- Looks for unread emails under the label in `.env` (default: `Applications`), matches common confirmation phrases, and marks the latest application as confirmed.

### 7) Cold email recruiters (optional)
- Put contacts in `recruiters.csv` with headers: `email,first_name,company,role`
- Authenticate Gmail API once to create `token.json` (follow Google Gmail API Python quickstart).
```bash
python cold_email.py
```

---

## Notes & Tips
- Prefer **small batches** and **randomized delays** to avoid flags.
- Consider Playwright **storage state** to avoid repeated logins.
- Greenhouse/Lever selectors are easiest to extend in `apply_runner.py`.
- Build a dashboard later (FastAPI + SQLite) if you want rich tracking.

## Disclaimer
This is a developer tool. You are responsible for complying with the Terms of Service of sites you interact with.


---

## Web Dashboard (FastAPI)

A lightweight UI to monitor jobs, mark statuses, view applications, and generate tailored cover letters from pasted JDs.

### Run
```bash
uvicorn app:app --reload
```
Open http://127.0.0.1:8000

### Pages
- **/**: Overview + quick status edits
- **/jobs**: Full job list (filter by status via query param)
- **/applications**: Application records
- **/cover**: Paste JD → generates a customized cover letter using `templates/cover.md`. The "hook" section is auto-derived from JD keywords.

> Tip: Keep Playwright apply flow running in another terminal while you review from the dashboard.
