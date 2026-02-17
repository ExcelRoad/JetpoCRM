import requests
import json

url = "http://127.0.0.1:8000/leads/api/webhook/elementor?token=jetpo_wp_678234901"

payload = {
    "form_name": "Footer Form",
    "fields": {
        "name": "עובד בדיקה",
        "email": "test@example.com",
        "phone": "050-1234567",
        "company": "חברת בדיקות",
        "description": "הודעת בדיקה מהאתר"
    }
}

headers = {
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
