# test_db.py
from storage import upload_pdf_to_gcs
from database import save_lead_to_gcp

print("1. Testing PDF upload to Google Cloud Storage...")
dummy_pdf_bytes = b"%PDF-1.4 Test Blueprint PDF Content..."
writer_name = "Cassandra Lee"
genre = "Thriller / Suspense"

pdf_url = upload_pdf_to_gcs(dummy_pdf_bytes, writer_name)
print(f"Generated PDF URL: {pdf_url}")

if pdf_url:
    print("🎉 SUCCESS: PDF uploaded to GCS successfully!")
else:
    print("❌ FAILURE: PDF upload to GCS failed.")

print("\n2. Testing Firestore Lead Logging with pdf_url...")
success = save_lead_to_gcp(
    writer_name=writer_name,
    email="cassandra@leeyieng.com",
    genre=genre,
    pdf_url=pdf_url or "Fallback Link"
)

if success:
    print("🎉 SUCCESS: Lead and valid pdf_url successfully written to GCP Firestore!")
else:
    print("❌ FAILURE: Failed to write lead to Firestore.")
