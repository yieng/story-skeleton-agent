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

    # 1. Try Streamlit Secrets
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return firestore.Client(credentials=credentials, database="story-skeleton-leads-db")
    except Exception:
        pass

    # 2. Try Environment Variables
    try:
        private_key = os.environ.get("private_key")
        client_email = os.environ.get("client_email")
        if private_key and client_email:
            creds_dict = {
                "type": os.environ.get("type", "service_account"),
                "project_id": os.environ.get("project_id", "story-skeleton-leads"),
                "private_key_id": os.environ.get("private_key_id"),
                "private_key": private_key.replace("\\n", "\n"),
                "client_email": client_email,
                "client_id": os.environ.get("client_id"),
                "auth_uri": os.environ.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": os.environ.get("token_uri", "https://oauth2.googleapis.com/token"),
                "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
                "client_x509_cert_url": os.environ.get("client_x509_cert_url")
            }
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return firestore.Client(credentials=credentials, database="story-skeleton-leads-db")
    except Exception as e:
        print(f"Error loading env Firestore credentials: {e}")

    # 3. Fallback to Local JSON File
    CREDENTIALS_PATH = "gcp_credentials.json"
    if os.path.exists(CREDENTIALS_PATH):
        try:
            credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
            return firestore.Client(credentials=credentials, database="story-skeleton-leads-db")
        except Exception as e:
            print(f"Error loading local credentials file: {e}")

    # 4. Ultimate fallback
    try:
        return firestore.Client(database="story-skeleton-leads-db")
    except Exception as e:
        print(f"Firestore initialization error: {e}")
        return None

def save_lead_to_gcp(writer_name: str, email: str, genre: str, pdf_url: str = "Local Download Used", blob_name: str = ""):
    if not ENABLE_FIRESTORE:
        print("Firestore is disabled.")
        return True
    
    db = get_firestore_client()
    if not db:
        print("Could not obtain Firestore client.")
        return False
    
    try:
        leads_ref = db.collection("leads")
        
        # Check if email already exists to prevent duplicates
        query = leads_ref.where("email", "==", email).limit(1).get()
        
        lead_data = {
            "writer_name": writer_name,
            "email": email,
            "genre": genre,
            "initial_pdf_url": pdf_url,
            "blob_name": blob_name,
            "access_expiry": datetime.now(datetime.timezone.utc) + timedelta(days=90),
            "timestamp": firestore.SERVER_TIMESTAMP,
            "subscribed": True
        }
        
        if len(query) > 0:
            # Update existing document so we don't create duplicates!
            doc_id = query[0].id
            leads_ref.document(doc_id).update(lead_data)
        else:
            # Create a brand new record
            leads_ref.add(lead_data)
            
        return True
    except Exception as e:
        print(f"Error saving lead to GCP: {e}")
        return False