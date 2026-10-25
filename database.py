# database.py
import os
import json
from datetime import datetime, timedelta
from google.cloud import firestore
from google.oauth2 import service_account

ENABLE_FIRESTORE = True

def get_firestore_client():
    if not ENABLE_FIRESTORE:
        return None
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return firestore.Client(credentials=credentials, database="story-skeleton-leads-db")
    except Exception:
        pass

    CREDENTIALS_PATH = "gcp_credentials.json"
    if os.path.exists(CREDENTIALS_PATH):
        try:
            credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
            return firestore.Client(credentials=credentials, database="story-skeleton-leads-db")
        except Exception as e:
            print(f"Error loading local credentials file: {e}")

    try:
        return firestore.Client(database="story-skeleton-leads-db")
    except Exception as e:
        print(f"Firestore initialization error: {e}")
        return None

def save_lead_to_gcp(writer_name: str, email: str, genre: str, pdf_url: str = "Local Download Used", blob_name: str = ""):
    """Saves subscriber lead, permanent blob path, initial signed URL, and 90-day expiry to Firestore."""
    if not ENABLE_FIRESTORE:
        print("Firestore is disabled.")
        return True
    
    db = get_firestore_client()
    if not db:
        print("Could not obtain Firestore client.")
        return False
    
    try:
        leads_ref = db.collection("leads")
        leads_ref.add({
            "writer_name": writer_name,
            "email": email,
            "genre": genre,
            "initial_pdf_url": pdf_url,
            "blob_name": blob_name,  # 👈 Permanent path for on-demand regeneration
            "access_expiry": datetime.utcnow() + timedelta(days=90),  # 3-month window
            "timestamp": firestore.SERVER_TIMESTAMP,
            "subscribed": True
        })
        return True
    except Exception as e:
        print(f"Error saving lead to GCP: {e}")
        return False
