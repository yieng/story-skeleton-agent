# mailer_sendgrid.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_via_sendgrid(recipient_email: str, recipient_name: str, pdf_download_link: str):
    api_key = os.environ.get("SENDGRID_API_KEY")
    sender_email = os.environ.get("SENDER_EMAIL", "noreply@the20percentfinish.com")
    
    subject = f"Your Story Structural Skeleton Blueprint is Ready, {recipient_name}!"
    content = f"""
    Hi {recipient_name},
    
    Thank you for using The Story Skeleton Architect for "The 20% Who Finish" platform. 
    
    You can securely download your customized structural skeleton blueprint and full session transcript here:
    {pdf_download_link}
    
    We respect your privacy—no spam ever, and you can unsubscribe at any time.
    
    Ready to turn this skeleton into a fully drafted manuscript? Book your free 1-on-1 Story Diagnostic Call with Cassandra here: https://calendly.com/yieng/15min-chat
    
    Keep writing,
    Cassandra Lee
    """
    
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        plain_text_content=content
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False
