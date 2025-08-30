
import os, re, datetime
from imapclient import IMAPClient
from models import SessionLocal, Application

PATTERNS = [
    re.compile(r"application received", re.I),
    re.compile(r"thank you for applying", re.I),
    re.compile(r"we received your application", re.I),
]

def run():
    db = SessionLocal()
    with IMAPClient(os.getenv("IMAP_HOST","imap.gmail.com")) as server:
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        server.select_folder(os.getenv("IMAP_LABEL","INBOX"))
        messages = server.search(["UNSEEN"])
        if not messages:
            print("No unseen messages.")
            return
        for msgid, data in server.fetch(messages, ["ENVELOPE", "RFC822.TEXT"]).items():
            subj = data[b"ENVELOPE"].subject.decode(errors="ignore") if data[b"ENVELOPE"].subject else ""
            body = data[b"RFC822.TEXT"].decode(errors="ignore")
            if any(p.search(subj) or p.search(body) for p in PATTERNS):
                app = db.query(Application).filter(Application.submitted==False).order_by(Application.id.desc()).first()
                if app:
                    app.submitted = True
                    app.confirmation_subject = subj
                    app.confirmation_at = datetime.datetime.utcnow()
                    db.commit()
        server.logout()

if __name__ == "__main__":
    run()
