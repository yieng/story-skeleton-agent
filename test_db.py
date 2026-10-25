# test_db.py
from storage import upload_pdf_to_gcs
from database import save_lead_to_gcp

print("1. Testing secure V4 Signed URL generation & PDF upload to GCS...")
dummy_pdf_bytes = b"%PDF-1.4 Secure Signed URL Test Blueprint Content..."
writer_name = "Cassandra Lee"
genre = "Thriller / Suspense"

signed_pdf_url = upload_pdf_to_gcs(dummy_pdf_bytes, writer_name)
print(f"Generated Signed URL:\n{signed_pdf_url}\n")

if signed_pdf_url and "GoogleAccessId" in signed_pdf_url:
    print("🎉 SUCCESS: Secure V4 Signed URL generated successfully!")
else:
    print("❌ FAILURE: Signed URL generation failed.")

print("\n2. Testing Firestore Lead Logging with signed pdf_url...")
success = save_lead_to_gcp(
    writer_name=writer_name,
    email="cassandra@leeyieng.com",
    genre=genre,
    pdf_url=signed_pdf_url or "Fallback Link"
)

if success:
    print("🎉 SUCCESS: Lead and signed pdf_url successfully written to GCP Firestore!")
else:
    print("❌ FAILURE: Failed to write lead to Firestore.")
