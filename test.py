import requests
import time

URL = 'http://127.0.0.1:5000/api/data'
TOTAL_REQUESTS = 15

print(f"Sending {TOTAL_REQUESTS} requests...\n")

for i in range(1, TOTAL_REQUESTS + 1):
    response = requests.get(URL)
    data = response.json()
    status = response.status_code

    if status == 429:
        print(f"Request {i}: BLOCKED 429 - {data['error']}")
    else:
        print(f"Request {i}: OK 200 - algorithm: {data['algorithm']}")

print("\nWaiting 15 seconds for tokens to refill...")
time.sleep(15)

print("\nSending 3 more requests after wait...\n")
for i in range(1, 4):
    response = requests.get(URL)
    status = response.status_code
    print(f"Request {i}: {'OK 200' if status == 200 else 'BLOCKED 429'}")