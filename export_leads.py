import csv
from google.cloud import firestore

db = firestore.Client(database="story-skeleton-leads-db")
leads_ref = db.collection("leads").stream()

with open("firestore_leads_export.csv", "w", newline="") as csvfile:
    fieldnames = ["writer_name", "email", "genre", "pdf_url", "timestamp", "subscribed"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for doc in leads_ref:
        data = doc.to_dict()
        writer.writerow(data)

print("Exported all Firestore leads to firestore_leads_export.csv successfully!")