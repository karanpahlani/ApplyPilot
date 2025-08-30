
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from models import SessionLocal, Job, Application
from jinja2 import Template
from datetime import datetime
import os, re, json, pathlib

app = FastAPI(title="ApplyPilot Dashboard")

BASE_DIR = pathlib.Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates" / "site"))

# /static (optional)
static_path = BASE_DIR / "static"
if not static_path.exists():
    static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

STOPWORDS = set("""a an the and or for to in of with on at from by is are was were be been being this that these those you your our their as it its we they he she him her i me my mine ours yours theirs about into over under out up down above below after before again further then once here there all any both each few more most other some such no nor not only own same so than too very can will just don don should now""".split())

def extract_hook(jd: str) -> str:
    # naive keyword extraction
    words = re.findall(r"[a-zA-Z][a-zA-Z+.#/-]*", jd.lower())
    freq = {}
    for w in words:
        if len(w) < 3 or w in STOPWORDS:
            continue
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]
    if not top:
        return "I mapped my recent work to your role's requirements and believe there's strong alignment."
    top_keys = ", ".join([k for k,_ in top[:3]])
    return f"I noticed emphasis on {top_keys}; I recently shipped systems with similar stack and scale (Go + AWS) and can contribute immediately."

def load_cover_template():
    path = BASE_DIR / "templates" / "cover.md"
    if not path.exists():
        raise HTTPException(status_code=500, detail="cover.md template missing")
    return path.read_text()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, status: Optional[str] = None):
    db = SessionLocal()
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    jobs = q.order_by(Job.id.desc()).limit(50).all()

    total = db.query(Job).count()
    applied = db.query(Job).filter(Job.status=="applied").count()
    confirmed = db.query(Job).filter(Job.status=="confirmed").count()
    new = db.query(Job).filter(Job.status=="new").count()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": jobs,
        "metrics": {"total": total, "new": new, "applied": applied, "confirmed": confirmed}
    })

@app.get("/jobs", response_class=HTMLResponse)
def list_jobs(request: Request, status: Optional[str] = None):
    db = SessionLocal()
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    jobs = q.order_by(Job.id.desc()).limit(200).all()
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs, "status": status})

@app.post("/jobs/{job_id}/status")
def update_status(job_id: int, new_status: str = Form(...)):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    job.status = new_status
    db.commit()
    return {"ok": True, "id": job_id, "status": new_status}

@app.get("/applications", response_class=HTMLResponse)
def list_apps(request: Request):
    db = SessionLocal()
    apps = db.query(Application).order_by(Application.id.desc()).limit(200).all()
    # join jobs for display
    job_map = {j.id: j for j in db.query(Job).filter(Job.id.in_([a.job_id for a in apps])).all()}
    return templates.TemplateResponse("applications.html", {"request": request, "apps": apps, "job_map": job_map})

@app.get("/cover", response_class=HTMLResponse)
def cover_form(request: Request, role: str = "", company: str = "", first_name: str = "", jd: str = ""):
    return templates.TemplateResponse("cover_form.html", {"request": request, "role": role, "company": company, "first_name": first_name, "jd": jd, "result": None})

@app.post("/cover", response_class=HTMLResponse)
def cover_generate(request: Request, role: str = Form(...), company: str = Form(...), first_name: str = Form(...), jd: str = Form(...)):
    tmpl_text = load_cover_template()
    hook = extract_hook(jd)
    # Load profile for links
    profile = json.loads((BASE_DIR / "data" / "static_profile.json").read_text())
    t = Template(tmpl_text)
    content = t.render(
        role=role,
        company=company,
        first_name=first_name or "there",
        hook=hook,
        portfolio=profile.get("portfolio",""),
        linkedin=profile.get("linkedin",""),
        calendly=os.getenv("SENDER_CALENDLY","")
    )
    return templates.TemplateResponse("cover_form.html", {"request": request, "role": role, "company": company, "first_name": first_name, "jd": jd, "result": content})

@app.get("/healthz")
def healthz():
    return {"ok": True, "time": datetime.utcnow().isoformat()}
