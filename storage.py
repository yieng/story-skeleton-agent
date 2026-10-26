    # storage.py
import os
from datetime import datetime, timedelta
from google.cloud import storage
from google.oauth2 import service_account

def get_storage_client():
    """Initializes Google Cloud Storage using Streamlit Secrets, environment variables, or local JSON."""
    
    # 1. Try Streamlit Secrets (for Streamlit Community Cloud)
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return storage.Client(credentials=credentials)
    except Exception:
        pass

    # 2. Try Environment Variables (if injected directly into cloud env or .env)
    try:
        private_key = os.environ.get("private_key")
        client_email = os.environ.get("client_email")
        project_id = os.environ.get("project_id", "story-skeleton-leads")
        
        if private_key and client_email:
            creds_dict = {
                "type": os.environ.get("type", "service_account"),
                "project_id": project_id,
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
            return storage.Client(credentials=credentials)
    except Exception as e:
        print(f"Error loading env GCS credentials: {e}")

    # 3. Fallback to Local JSON File (for local Mac testing)
    CREDENTIALS_PATH = "gcp_credentials.json"
    if os.path.exists(CREDENTIALS_PATH):
        try:
            return storage.Client.from_service_account_json(CREDENTIALS_PATH)
        except Exception as e:
            print(f"Error loading local GCS credentials: {e}")

    # 4. Ultimate fallback to ADC
    try:
        return storage.Client()
    except Exception as e:
        print(f"GCS client initialization error: {e}")
        return None

def upload_pdf_to_gcs(pdf_bytes: bytes, writer_name: str):
    """Uploads PDF bytes to GCS with a unique timestamp. Returns (signed_url, blob_name)."""
    client = get_storage_client()
    if not client:
        print("Could not obtain GCS client.")
        return None, None
    
    bucket_name = os.environ.get("GCS_BUCKET_NAME", "story-skeleton-pdfs")
    
    try:
        bucket = client.bucket(bucket_name)
        safe_name = "".join(c for c in writer_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"blueprints/{safe_name}_{timestamp}_story_skeleton.pdf"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )
        return signed_url, blob_name
    except Exception as e:
        print(f"Error generating signed URL: {e}")
        return None, None

def regenerate_signed_url(blob_name: str) -> str:
    """Takes a persistent blob path and generates a fresh 7-day V4 Signed URL on demand."""
    client = get_storage_client()
    if not client:
        return None
    
    bucket_name = os.environ.get("GCS_BUCKET_NAME", "story-skeleton-pdfs")
    
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        if not blob.exists():
            return None
            
        fresh_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )
        return fresh_url
    except Exception as e:
        print(f"Error regenerating signed URL: {e}")
        return None