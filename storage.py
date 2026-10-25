# storage.py
import os
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

def upload_pdf_to_gcs(pdf_bytes: bytes, writer_name: str) -> str:
    """Uploads generated PDF bytes to Google Cloud Storage and returns a public URL."""
    client = get_storage_client()
    if not client:
        print("Could not obtain GCS client.")
        return None
    
    bucket_name = os.environ.get("GCS_BUCKET_NAME", "story-skeleton-pdfs")
    
    try:
        bucket = client.bucket(bucket_name)
        safe_name = "".join(c for c in writer_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
        blob_name = f"blueprints/{safe_name}_story_skeleton.pdf"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        
        return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
    except Exception as e:
        print(f"Error uploading PDF to GCS: {e}")
        return None
