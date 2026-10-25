from datetime import datetime
from google.cloud import firestore
from storage import get_storage_client
from datetime import timedelta

db = firestore.Client(database="story-skeleton-leads-db")
leads = db.collection("leads").stream()

now = datetime.utcnow()

for lead in leads:
    data = lead.to_dict()
    email = data.get("email")
    writer_name = data.get("writer_name")
    expiry = data.get("access_expiry") # Firestore timestamp
    
    # Check if within the 3-month (90-day) window
    if expiry and now < expiry.replace(tzinfo=None):
        # 1. Still within 90 days: Generate a fresh 7-day signed URL on the fly
        client = get_storage_client()
        bucket = client.bucket("story-skeleton-pdfs")
        # Assuming you store the blob_name in Firestore, e.g., "blueprints/Cassandra_Lee_20261025_...pdf"
        blob_name = data.get("blob_name") 
        blob = bucket.blob(blob_name)
        
        fresh_signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )
        
        # Email copy with active download link
        email_body = f"""
        Hi {writer_name},
        
        You're receiving this because you generated a Story Skeleton Blueprint at The Story Skeleton Architect. 
        Here is your active blueprint download link (valid for the next 7 days): {fresh_signed_url}
        
        As a reminder, your cloud backup remains accessible in your dashboard for 90 days following your signup.
        
        Best regards,
        Cassandra
        """
    else:
        # 2. Past 90 days: Phase out the download link gracefully
        email_body = f"""
        Hi {writer_name},
        
        You're receiving this because you generated a Story Skeleton Blueprint at The Story Skeleton Architect. 
        Your 90-day complimentary cloud backup window for this specific blueprint has recently expired. 
        
        Feel free to visit the app anytime to generate a brand new master structural blueprint!
        
        Best regards,
        Cassandra
        """
    
    # Send email via your chosen dispatch method (SendGrid / SMTP)
    print(f"Dispatching email to {email}...")
