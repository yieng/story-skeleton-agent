# test_db.py
from pdfmaker import create_styled_pdf
from storage import upload_pdf_to_gcs
from database import save_lead_to_gcp

print("1. Generating real styled PDF blueprint...")
real_pdf_bytes = create_styled_pdf(
    title_text="Story Skeleton Blueprint & Transcript — Cassandra Lee",
    full_transcript_markdown="""# INITIAL STORY INPUTS
- **Writer Name:** Cassandra Lee
- **Genre:** Thriller / Suspense
- **Inciting Incident:** A mysterious encrypted flash drive arrives at the door.

---
# FINAL MASTER STRUCTURAL BLUEPRINT
**ACT I:** The ordinary world is shattered.
**ACT II-A:** Crossing into danger.
**ACT II-B:** The dark night of the soul.
**ACT III:** The final courtroom showdown.
"""
)

print("2. Uploading real PDF to Google Cloud Storage & generating V4 Signed URL...")
signed_pdf_url = upload_pdf_to_gcs(real_pdf_bytes, "Cassandra Lee")
print(f"Generated Signed URL:\n{signed_pdf_url}\n")

if signed_pdf_url and "X-Goog-Signature" in signed_pdf_url:
    print("🎉 SUCCESS: Secure V4 Signed URL generated successfully!")
else:
    print("❌ FAILURE: Signed URL generation failed.")

print("\n3. Testing Firestore Lead Logging with signed pdf_url...")
success = save_lead_to_gcp(
    writer_name="Cassandra Lee",
    email="cassandra@leeyieng.com",
    genre="Thriller / Suspense",
    pdf_url=signed_pdf_url
)

if success:
    print("🎉 SUCCESS: Lead and signed pdf_url successfully written to GCP Firestore!")
else:
    print("❌ FAILURE: Failed to write lead to Firestore.")
