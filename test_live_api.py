
import getpass
from datetime import date, datetime

import requests


BASE_URL = "https://foundit-backend-1c64.onrender.com"

passed = 0
failed = 0


def check(name, response, expected):
    global passed, failed

    if response.status_code == expected:
        print(f"PASS: {name} ({response.status_code})")
        passed += 1
    else:
        print(
            f"FAIL: {name} "
            f"(expected {expected}, got {response.status_code})"
        )
        try:
            print("     ", response.json())
        except ValueError:
            print("     ", response.text[:200])
        failed += 1


def run_tests():
    global passed, failed

    admin_email = input("Admin email: ").strip()
    admin_password = getpass.getpass("Admin password: ")

    admin = requests.Session()
    guest = requests.Session()

    category_id = None
    lost_item_id = None
    found_item_id = None

    unique = datetime.now().strftime("%Y%m%d%H%M%S")
    category_name = f"API Test Category {unique}"

    try:
        print("\n--- PUBLIC ENDPOINTS ---")

        check("API root", guest.get(BASE_URL + "/"), 200)
        check(
            "Get categories",
            guest.get(BASE_URL + "/api/categories"),
            200
        )
        check(
            "Get lost items",
            guest.get(BASE_URL + "/api/lost-items"),
            200
        )
        check(
            "Invalid lost-item pagination",
            guest.get(BASE_URL + "/api/lost-items?page=0"),
            400
        )
        check(
            "Get found items",
            guest.get(BASE_URL + "/api/found-items"),
            200
        )

        print("\n--- AUTHENTICATION ---")

        check(
            "Login with invalid credentials",
            guest.post(
                BASE_URL + "/login",
                json={
                    "email": admin_email,
                    "password": "DefinitelyWrongPassword123!"
                }
            ),
            401
        )

        login_response = admin.post(
            BASE_URL + "/login",
            json={
                "email": admin_email,
                "password": admin_password
            }
        )

        check("Admin login", login_response, 200)

        if login_response.status_code != 200:
            print("\nCannot continue without a successful admin login.")
            return

        check(
            "Check active session",
            admin.get(BASE_URL + "/check_session"),
            200
        )

        print("\n--- ACCESS CONTROL ---")

        check(
            "Guest cannot create category",
            guest.post(
                BASE_URL + "/api/categories",
                json={"name": category_name}
            ),
            401
        )

        check(
            "Guest cannot create lost item",
            guest.post(
                BASE_URL + "/api/lost-items",
                json={}
            ),
            401
        )

        check(
            "Guest cannot create found item",
            guest.post(
                BASE_URL + "/api/found-items",
                json={}
            ),
            401
        )

        print("\n--- ADMIN ENDPOINTS ---")

        check(
            "Get admin users",
            admin.get(BASE_URL + "/api/admin/users"),
            200
        )

        check(
            "Get all admin lost items",
            admin.get(BASE_URL + "/api/admin/lost-items"),
            200
        )

        check(
            "Get all admin found items",
            admin.get(BASE_URL + "/api/admin/found-items"),
            200
        )

        check(
            "Get all claims as admin",
            admin.get(BASE_URL + "/api/claims"),
            200
        )

        check(
            "Get my claims",
            admin.get(BASE_URL + "/api/claims/my"),
            200
        )

        check(
            "Get notifications",
            admin.get(BASE_URL + "/api/notifications"),
            200
        )

        print("\n--- CATEGORY TESTS ---")

        create_category = admin.post(
            BASE_URL + "/api/categories",
            json={"name": category_name}
        )

        check("Create category", create_category, 201)

        if create_category.status_code != 201:
            print("Cannot continue item tests without a category.")
            return

        category_id = create_category.json()["category"]["id"]

        check(
            "Get categories as admin",
            admin.get(BASE_URL + "/api/categories"),
            200
        )

        check(
            "Reject duplicate category",
            admin.post(
                BASE_URL + "/api/categories",
                json={"name": category_name}
            ),
            409
        )

        print("\n--- LOST ITEM TESTS ---")

        lost_data = {
            "item_name": "API Test Lost Item",
            "description": "Temporary item created by automated testing",
            "location": "Test Location",
            "date_lost": date.today().isoformat(),
            "category_id": category_id
        }

        create_lost = admin.post(
            BASE_URL + "/api/lost-items",
            json=lost_data
        )

        check("Create lost item", create_lost, 201)

        if create_lost.status_code == 201:
            lost_item_id = create_lost.json()["item"]["id"]

            check(
                "Get one lost item",
                admin.get(
                    f"{BASE_URL}/api/lost-items/{lost_item_id}"
                ),
                200
            )

            check(
                "Update lost item",
                admin.patch(
                    f"{BASE_URL}/api/lost-items/{lost_item_id}",
                    json={"item_name": "Updated API Test Lost Item"}
                ),
                200
            )

        check(
            "Search lost items",
            admin.get(
                BASE_URL + "/api/lost-items",
                params={"search": "API Test"}
            ),
            200
        )

        check(
            "Missing lost item returns 404",
            admin.get(BASE_URL + "/api/lost-items/999999999"),
            404
        )

        print("\n--- FOUND ITEM TESTS ---")

        found_data = {
            "item_name": "API Test Found Item",
            "description": "Temporary item created by automated testing",
            "location": "Test Location",
            "date_found": date.today().isoformat(),
            "category_id": category_id
        }

        create_found = admin.post(
            BASE_URL + "/api/found-items",
            json=found_data
        )

        check("Create found item", create_found, 201)

        if create_found.status_code == 201:
            found_item_id = create_found.json()["item"]["id"]

            check(
                "Get one found item",
                admin.get(
                    f"{BASE_URL}/api/found-items/{found_item_id}"
                ),
                200
            )

            check(
                "Update found item",
                admin.patch(
                    f"{BASE_URL}/api/found-items/{found_item_id}",
                    json={"item_name": "Updated API Test Found Item"}
                ),
                200
            )

        check(
            "Search found items",
            admin.get(
                BASE_URL + "/api/found-items",
                params={"search": "API Test"}
            ),
            200
        )

        check(
            "Missing found item returns 404",
            admin.get(BASE_URL + "/api/found-items/999999999"),
            404
        )

    except requests.RequestException as error:
        print(f"\nCONNECTION ERROR: {error}")

    except (KeyError, ValueError) as error:
        print(f"\nTEST SCRIPT ERROR: {error}")

    finally:
        print("\n--- CLEANING UP TEST DATA ---")

        if lost_item_id is not None:
            check(
                "Delete temporary lost item",
                admin.delete(
                    f"{BASE_URL}/api/lost-items/{lost_item_id}"
                ),
                200
            )

        if found_item_id is not None:
            check(
                "Delete temporary found item",
                admin.delete(
                    f"{BASE_URL}/api/found-items/{found_item_id}"
                ),
                200
            )

        if category_id is not None:
            check(
                "Delete temporary category",
                admin.delete(
                    f"{BASE_URL}/api/categories/{category_id}"
                ),
                200
            )

        admin.delete(BASE_URL + "/logout")

        print("\n==============================")
        print("       TEST RESULTS")
        print("==============================")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total:  {passed + failed}")
        print("==============================")


if __name__ == "__main__":
    run_tests()
