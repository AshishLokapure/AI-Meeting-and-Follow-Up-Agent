"""
smtp_test.py — Run from backend/ to diagnose SMTP issues.
    python smtp_test.py
"""
import sys, os, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

from dotenv import load_dotenv
load_dotenv(".env")

from app.core.settings import get_settings
s = get_settings()

print("=" * 60)
print("SMTP CONFIGURATION")
print("=" * 60)
print(f"  MAIL_HOST     : {s.mail_host}")
print(f"  MAIL_PORT     : {s.mail_port}")
print(f"  MAIL_USERNAME : {s.mail_username}")
print(f"  MAIL_FROM     : {s.mail_from}")
print(f"  MAIL_FROM_NAME: {s.mail_from_name}")
print(f"  MAIL_PASSWORD : {'SET (' + str(len(s.mail_password)) + ' chars)' if s.mail_password else 'EMPTY !!!'}")
print()

# ── Step 1: Check all required fields are set ─────────────────────────────────
errors = []
if not s.mail_host:       errors.append("MAIL_HOST is empty")
if not s.mail_username:   errors.append("MAIL_USERNAME is empty")
if not s.mail_password:   errors.append("MAIL_PASSWORD is empty")
if not s.mail_from:       errors.append("MAIL_FROM is empty")

if errors:
    print("CONFIG ERRORS:")
    for e in errors:
        print(f"  !! {e}")
    sys.exit(1)

# ── Step 2: Raw SMTP connection test ──────────────────────────────────────────
from smtplib import SMTP, SMTPException
print("Step 1: Connecting to SMTP server...")
try:
    with SMTP(s.mail_host, s.mail_port, timeout=15) as smtp:
        code, msg = smtp.ehlo()
        print(f"  EHLO      : {code} {msg.decode(errors='replace')[:80]}")

        code, msg = smtp.starttls()
        print(f"  STARTTLS  : {code} {msg.decode(errors='replace')[:80]}")

        code, msg = smtp.ehlo()
        print(f"  EHLO2     : {code} {msg.decode(errors='replace')[:80]}")

        code, msg = smtp.login(s.mail_username, s.mail_password)
        print(f"  LOGIN     : {code} {msg.decode(errors='replace')[:80]}")
        print()
        print("  [OK] SMTP login successful!")
        print()

        # ── Step 3: Send a real test email ────────────────────────────────────
        print("Step 2: Sending test email...")
        from email.message import EmailMessage
        msg_obj = EmailMessage()
        msg_obj["Subject"] = "AI Meeting Agent — SMTP Test"
        msg_obj["From"]    = f"{s.mail_from_name} <{s.mail_from}>"
        msg_obj["To"]      = s.mail_from   # send to yourself
        msg_obj.set_content("This is a test email from AI Meeting Agent SMTP diagnostic.")
        msg_obj.add_alternative(
            "<h2>SMTP Test</h2><p>If you see this, your Brevo SMTP is working correctly.</p>",
            subtype="html"
        )
        smtp.send_message(msg_obj)
        print(f"  [OK] Test email sent to {s.mail_from}")
        print()
        print("=" * 60)
        print("  ALL CHECKS PASSED — Email system is working!")
        print("=" * 60)

except SMTPException as e:
    print(f"\n  [FAIL] SMTPException: {e}")
    traceback.print_exc()
    print()
    print("DIAGNOSIS:")
    msg_str = str(e).lower()
    if "535" in str(e) or "authentication" in msg_str:
        print("  -> 535 Auth failed. Your MAIL_USERNAME or MAIL_PASSWORD is wrong.")
        print("     Go to Brevo -> SMTP & API -> SMTP tab -> copy the exact login/password.")
    elif "525" in str(e) or "unauthorized ip" in msg_str:
        print("  -> 525 Unauthorized IP. Your machine's IP is not whitelisted in Brevo.")
        print()
        try:
            import urllib.request
            public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()
            print(f"  -> Your public IP is: {public_ip}")
        except Exception:
            print("  -> Could not detect public IP. Visit https://whatismyip.com")
        print()
        print("  FIX: Log in to https://app.brevo.com")
        print("       Settings -> Senders & IPs -> Dedicated IPs -> Authorized IPs -> Add IP")
        print("       OR use smtp-relay.brevo.com on port 587 with your API key as password.")
    elif "550" in str(e) or "sender" in msg_str:
        print("  -> 550 Sender rejected. MAIL_FROM is not verified in Brevo.")
        print("     Go to Brevo -> Senders & IPs -> Senders -> verify your email.")
    elif "connection" in msg_str or "timeout" in msg_str:
        print("  -> Connection failed. Port 587 may be blocked by your firewall/ISP.")
        print("     Try: telnet smtp-relay.brevo.com 587")
    sys.exit(1)

except Exception as e:
    print(f"\n  [FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
