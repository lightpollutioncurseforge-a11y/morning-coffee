import datetime as dt, json, os, re, sys, urllib.error, urllib.request
from zoneinfo import ZoneInfo

date = sys.argv[1]
key, to = os.environ.get("RESEND_API_KEY"), os.environ.get("MAIL_TO")
if not key or not to:
    sys.exit("RESEND_API_KEY or MAIL_TO is not set")
html = open(f"issues/{date}/postcard.html", encoding="utf-8").read()
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
body = {"from": "Morning Coffee <onboarding@resend.dev>", "to": [to], "subject": title, "html": html}
# Arrive at 8:30 Eastern on the issue's date, or at once if that has passed.
when = dt.datetime.fromisoformat(date).replace(hour=8, minute=30, tzinfo=ZoneInfo("America/New_York"))
if not os.environ.get("SEND_NOW") and when > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=2):
    body["scheduled_at"] = when.isoformat()
req = urllib.request.Request("https://api.resend.com/emails", json.dumps(body).encode(), {
    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    "User-Agent": "morning-coffee/1.0", "Idempotency-Key": f"morning-coffee-{date}-{os.environ.get('SEND_NONCE','')}"})
try:
    print(urllib.request.urlopen(req, timeout=30).read().decode(), "scheduled:", body.get("scheduled_at", "now"))
except urllib.error.HTTPError as e:
    sys.exit(f"Resend {e.code}: {e.read().decode()}")
