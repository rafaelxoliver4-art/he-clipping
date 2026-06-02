import os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from email_sender import _load_env, send
_load_env()
print("FROM:", os.environ.get("FROM_EMAIL"))
report = {"Deliverability test": [
    {"ticker": "TEST",
     "headline": "If you can read this, email delivery from the H&E pipeline is working.",
     "source": "H&E pipeline", "link": "", "date": ""}
]}
try:
    n = send(report, [], recipients=["rafaelxoliver4@gmail.com"])
    print(f"SMTP accepted — sent {n} item(s) to rafaelxoliver4@gmail.com")
except Exception as e:
    print(f"SEND FAILED: {type(e).__name__}: {e}")
