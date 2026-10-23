import requests

token = requests.post("http://127.0.0.1:8000/api/auth/login", json={"username_or_email": "inspector", "password": "Inspector@123"}).json()["access_token"]
items = requests.get("http://127.0.0.1:8000/api/inspections/5/ocr", headers={"Authorization": f"Bearer {token}"}).json()
for i in items:
    print(f"{i['line_number']}: {i['text']}")
