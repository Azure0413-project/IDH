import requests
url = 'http://10.11.29.18/php/dialysislist.php'
print(f"test API: {url}")
print("waiting for request")

try:
    response = requests.get(url, params = {'date': '2026-03-17'}, timeout=5)
    print(f"connect successfully HTTP code{response.status_code}")
    print(response.text[:100])

except requests.exceptions.Timeout:
    print("wrong:timeout")
except requests.exceptions.ConnectionError as e:
    print(f"error message: {e}")
except Exception as e:
    print(f"error unknown: {e}")