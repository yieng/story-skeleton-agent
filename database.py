# database.py
import os
from google.cloud import firestore

# Point explicitly to your downloaded service account JSON credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_credentials.json"

def get_firestore_client():
    """Initializes and returns the Firestore client targeting your custom database ID."""
    try:
        # Pass your custom database ID here instead of leaving it blank!
        db = firestore.Client(database="story-skeleton-leads-db")
        return db
    except Exception as e:
        print(f"Firestore initialization error: {e}")
        return None

def save_lead_to_gcp(writer_name: str, email: str, genre: str):
    """Saves a verified subscriber lead to Google Cloud Firestore."""
    db = get_firestore_client()
    if not db:
        return False
    
    try:
        leads_ref = db.collection("leads")
        leads_ref.add({
            "writer_name": writer_name,
            "email": email,
            "genre": genre,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "verified": True
        })
        return True
    except Exception as e:
        print(f"Error saving lead to GCP: {e}")
        return False