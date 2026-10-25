# mailer_kit.py
import os
import requests

def subscribe_via_kit(recipient_email: str, recipient_name: str, pdf_download_link: str):
    api_key = os.environ.get("KIT_API_KEY")
    form_id = os.environ.get("KIT_FORM_ID")
    
    # Kit v3 API endpoint for adding a subscriber to a form/sequence
    url = f"https://api.convertkit.com/v3/forms/{form_id}/subscribe"
    
    payload = {
        "api_key": api_key,
        "email": recipient_email,
        "first_name": recipient_name,
        # You can pass custom fields or trigger automations that email the PDF link automatically
        "fields": {
            "pdf_download_link": pdf_download_link
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Kit API error: {e}")
        return False