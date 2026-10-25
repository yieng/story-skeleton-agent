# mailer_native.py
import os
import smtplib
import random
import json
from email.message import EmailMessage
import streamlit as st
from itsdangerous import URLSafeTimedSerializer

# Secret salt for token generation
SECRET_SALT = "story-skeleton-secure-optin-salt"

def get_serializer():
    """Helper to get the itsdangerous serializer using app secrets or environment."""
    try:
        secret_key = st.secrets.get("SECRET_KEY", "fallback_secret_key_123")
    except Exception:
        secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key_123")
    return URLSafeTimedSerializer(secret_key, salt=SECRET_SALT)

def generate_verification_token(email: str, name: str) -> str:
    """Generates a secure, time-sensitive token for the user's email and name."""
    serializer = get_serializer()
    return serializer.dumps({"email": email, "name": name})

def verify_token(token: str, max_age: int = 86400):
    """Verifies the token (default 24-hour expiry) and returns the user data payload."""
    serializer = get_serializer()
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def get_random_html_template(recipient_name: str, verification_link: str) -> tuple:
    """Loads templates from success_templates.json and picks a random one, formatting placeholders."""
    json_path = "success_templates.json"
    
    # Fallback template if file is missing
    default_template = (
        f"Your Story Skeleton Blueprint is Ready, {recipient_name}",
        f"""
        <div style="font-family: Arial, sans-serif; color: #334155; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #1E293B;">Almost There, {recipient_name}!</h2>
            <p>Please click the button below to confirm your subscription and unlock your PDF:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" style="background-color: #2563EB; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Confirm Email</a>
            </div>
        </div>
        """
    )
    
    if not os.path.exists(json_path):
        return default_template
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            templates = data.get("templates", [])
            if not templates:
                return default_template
                
            chosen = random.choice(templates)
            subject = chosen["subject"].format(recipient_name=recipient_name)
            html_body = chosen["html_body"].format(recipient_name=recipient_name, verification_link=verification_link)
            return subject, html_body
    except Exception as e:
        print(f"Error loading success_templates.json: {e}")
        return default_template

def send_verification_email(recipient_email: str, recipient_name: str, base_url: str) -> bool:
    """Generates a secure verification link and sends it using a randomly selected anti-spam template from JSON."""
    
    token = generate_verification_token(recipient_email, recipient_name)
    verification_link = f"{base_url}/?verify={token}"
    
    # Pick a random template layout from external JSON
    subject, html_content = get_random_html_template(recipient_name, verification_link)
    
    # Pull SMTP configuration securely
    try:
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = int(st.secrets["SMTP_PORT"])
        smtp_user = st.secrets["SMTP_USER"]
        smtp_password = st.secrets["SMTP_PASSWORD"]
        sender_email = st.secrets.get("SENDER_EMAIL", smtp_user)
    except Exception:
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        sender_email = os.environ.get("SENDER_EMAIL", smtp_user)

    if not smtp_user or not smtp_password:
        print("SMTP credentials are not configured.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email
    
    # Plain text fallback
    msg.set_content(f"Hi {recipient_name},\n\nPlease confirm your email by clicking this link: {verification_link}\n\nOnce confirmed, your blueprint download will be unlocked.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Native SMTP error: {e}")
        return False