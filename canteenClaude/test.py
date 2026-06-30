# insert_test.py
import requests

url = "http://127.0.0.1:5000/api/menu/"
payload = {
    "name": "Laksa",
    "price": 5.50,
    "category": "Mains",       # ADD THIS LINE
    "description": "Rich curry coconut broth",
    "is_available": True
}
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response JSON: {response.json()}")



# # Change the number at the end to match an existing ID in your database
# target_id = 1 
# url = f"http://127.0.0.1:5000/api/menu/{target_id}"

# response = requests.delete(url)

# print(f"Status Code: {response.status_code}")
# print(f"Response JSON: {response.json()}")