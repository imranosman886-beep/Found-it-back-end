
import json
from getpass import getpass
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError
from http.cookiejar import CookieJar

BASE_URL = "https://foundit-backend-1c64.onrender.com"

opener = build_opener(HTTPCookieProcessor(CookieJar()))

email = input("Admin email: ")
password = getpass("Admin password: ")


def post(endpoint, payload):
    request = Request(
        BASE_URL + endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with opener.open(request) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


status, data = post("/login", {
    "email": email,
    "password": password
})

if status != 200:
    print("Login failed:", data)
    raise SystemExit

if data.get("user", {}).get("role") != "admin":
    print("This account is not an admin.")
    raise SystemExit

print("\nAdmin login successful!")

categories = [
    "Electronics",
    "Clothing",
    "Bags",
    "Accessories",
    "Books & Stationery",
    "Keys",
    "Documents",
    "Other"
]

for name in categories:
    status, result = post("/api/categories", {"name": name})

    if status == 201:
        print("Created:", name)
    elif status == 409:
        print("Already exists:", name)
    else:
        print("Error creating", name, ":", result)

print("\nFinished!")
