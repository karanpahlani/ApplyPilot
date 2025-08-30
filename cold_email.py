
from __future__ import annotations
import base64, os, csv
from email.message import EmailMessage
from jinja2 import Template
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("gmail", "v1", credentials=creds)

TEMPLATE = """Subject: {{ role }} @ {{ company }}

Hi {{ first_name }},

I’m Karan, a Senior Backend Engineer (Go + AWS, DynamoDB, S3, SNS/SQS) who scaled Fetch Rewards from ~1M → 12M MAUs.
{{ hook }}

Would love to speak about {{ role }} on your team. Quick profile:
- Portfolio: {{ portfolio }}
- LinkedIn: {{ linkedin }}

If useful, grab time here: {{ calendly }}
Best,
Karan
"""

def send(to_addr, subject, body):
    svc = gmail_service()
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": encoded}).execute()

def main():
    with open("recruiters.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            t = Template(TEMPLATE)
            hook = f"I noticed {r.get('company','your company')} uses Go/event-driven infra; I recently shipped duplicate e-receipt detection that increased blocks by 100x."
            body_full = t.render(
                role=r.get("role","Software Engineer"),
                company=r.get("company",""),
                first_name=r.get("first_name","there"),
                hook=hook,
                portfolio=os.getenv("PORTFOLIO","https://pahlani.com"),
                linkedin=os.getenv("LINKEDIN_PROFILE","https://www.linkedin.com/in/karanpahlani"),
                calendly=os.getenv("SENDER_CALENDLY","https://calendly.com/pahlani/30min")
            )
            subject, content = body_full.split("\n", 1)
            send(r["email"], subject.replace("Subject: ", ""), content.strip())

if __name__ == "__main__":
    main()
