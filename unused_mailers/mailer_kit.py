# mailer_kit.py
import os
import requests
import streamlit as st

def subscribe_via_kit(recipient_email: str, recipient_name: str, pdf_download_link: str):
    """Subscribes the lead to Kit (ConvertKit) which triggers their automated double-opt-in and PDF delivery."""
    
    # Pull API key and Form ID safely from Streamlit Secrets or local environment
    try:
        api_key = st.secrets["KIT_API_KEY"]
        form_id = st.secrets["KIT_FORM_ID"]
    except Exception:
        api_key = os.environ.get("KIT_API_KEY")
        form_id = os.environ.get("KIT_FORM_ID")
        
    if not api_key or not form_id:
        print("Kit API Key or Form ID missing.")
        return False
    
    # Kit v3 API endpoint for adding a subscriber to a specific form
    url = f"https://api.convertkit.com/v3/forms/{form_id}/subscribe"
    
    payload = {
        "api_key": api_key,
        "email": recipient_email,
        "first_name": recipient_name,
        # Pass custom fields if you want to store the PDF link directly in Kit's subscriber profile
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