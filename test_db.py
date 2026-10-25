# test_db.py
from database import save_lead_to_gcp

print("Testing connection to GCP Firestore...")

success = save_lead_to_gcp(
    writer_name="Cassandra Lee",
    email="cassandra@leeyieng.com",
    genre="Thriller / Suspense"
)

if success:
    print("🎉 SUCCESS: Test lead successfully written to GCP Firestore!")
else:
    print("❌ FAILURE: Check your credentials file and database ID.")
