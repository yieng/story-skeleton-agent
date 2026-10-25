# storage.py
import os
from datetime import datetime, timedelta
from google.cloud import storage
from google.oauth2 import service_account

def get_storage_client():
    """Initializes Google Cloud Storage using Streamlit Secrets or local credentials."""
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return storage.Client(credentials=credentials)
    except Exception:
        pass

    CREDENTIALS_PATH = "gcp_credentials.json"
    if os.path.exists(CREDENTIALS_PATH):
        try:
            return storage.Client.from_service_account_json(CREDENTIALS_PATH)
        except Exception as e:
            print(f"Error loading local GCS credentials: {e}")

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
