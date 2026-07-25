import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api/v1"

# Login
data = json.dumps({"email": "ashishlokapure19@gmail.com", "password": "Demo@1234"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=data, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req) as r:
    token = json.loads(r.read())["tokens"]["access_token"]
print("LOGIN OK")

# GET employees
req2 = urllib.request.Request(f"{BASE}/employees", headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req2) as r:
        body = json.loads(r.read())
        print("GET OK, count:", len(body.get("employees", body)))
except urllib.error.HTTPError as e:
    err = e.read().decode("utf-8", errors="replace")
    print("GET ERROR", e.code, err[:600])

# POST employee - correct schema
payload = json.dumps({
    "first_name": "Rahul",
    "last_name": "Mehta",
    "email": "rahul.diag99@example.com",
    "password": "Test@1234",
    "role": "developer",
    "status": "active"
}).encode()
req3 = urllib.request.Request(
    f"{BASE}/employees", data=payload,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
try:
    with urllib.request.urlopen(req3) as r:
        print("POST OK:", json.loads(r.read()))
except urllib.error.HTTPError as e:
    err = e.read().decode("utf-8", errors="replace")
    print("POST ERROR", e.code, err[:600])

# POST employee - OLD schema (what frontend sends)
payload_old = json.dumps({
    "name": "Rahul Mehta",
    "email": "rahul.old99@example.com",
    "phone": None,
    "department": "Engineering",
    "designation": "Developer"
}).encode()
req4 = urllib.request.Request(
    f"{BASE}/employees", data=payload_old,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
try:
    with urllib.request.urlopen(req4) as r:
        print("POST OLD OK:", json.loads(r.read()))
except urllib.error.HTTPError as e:
    err = e.read().decode("utf-8", errors="replace")
    print("POST OLD ERROR", e.code, err[:600])
