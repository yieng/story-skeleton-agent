# broadcast_engine.py
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from google.cloud import firestore
from storage import regenerate_signed_url  # Our self-healing helper!

def run_newsletter_broadcast():
    db = firestore.Client(database="story-skeleton-leads-db")
    leads_ref = db.collection("leads").stream()
    
    now = datetime.utcnow()
    
    for doc in leads_ref:
        lead = doc.to_dict()
        email = lead.get("email")
        writer_name = lead.get("writer_name")
        blob_name = lead.get("blob_name")
        access_expiry = lead.get("access_expiry")
        
        # Check if within the 90-day window
        if access_expiry and now < access_expiry.replace(tzinfo=None):
            # 🔄 SELF-HEALING: Mint a fresh 7-day signed URL on the fly!
            active_pdf_link = regenerate_signed_url(blob_name)
            
            download_section = f"""
            <p>Need to reference your saved blueprint? Here is your fresh download link (valid for the next 7 days):</p>
            <p><a href="{active_pdf_link}" style="color: #2563EB; font-weight: bold;">Download Your Story Skeleton PDF</a></p>
            <p style="font-size: 12px; color: #64748B;">Your 90-day complimentary cloud backup window remains active.</p>
            """
        else:
            # Past 90 days: Gracefully phase out the link
            download_section = """
            <p style="font-size: 12px; color: #64748B;">Your 90-day complimentary cloud backup window for your initial blueprint has expired. Feel free to visit the app anytime to generate a brand new master structural blueprint!</p>
            """
            
        # Compose email payload
        msg = EmailMessage()
        msg["Subject"] = f"Creative SOP: Breaking Through the Middle-Book Swamp, {writer_name}"
        msg["From"] = os.environ.get("SENDER_EMAIL", "info@leeyieng.com")
        msg["To"] = email
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #334155; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Hello {writer_name},</h2>
            <p>Here is your weekly tactical breakdown on narrative mechanics...</p>
            {download_section}
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 20px 0;">
            <p style="font-size: 12px; color: #94A3B8;">
                You're receiving this because you generated a Story Skeleton Blueprint at The Story Skeleton Architect. 
                To unsubscribe, simply reply to this email with "Remove".
            </p>
        </div>
        """
        
        msg.set_content(f"Hi {writer_name},\n\nCheck out this week's writing framework...")
        msg.add_alternative(html_content, subtype="html")
        
        # Send via your native SMTP configuration
        try:
            with smtplib.SMTP(os.environ.get("SMTP_SERVER", "smtp.zoho.com"), int(os.environ.get("SMTP_PORT", 587))) as server:
                server.starttls()
                server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD"))
                server.send_message(msg)
            print(f"Successfully sent broadcast to {email}")
        except Exception as e:
            print(f"Failed to send to {email}: {e}")

if __name__ == "__main__":
    run_newsletter_broadcast()