import smtplib
import os
from email.message import EmailMessage
from utils.logger import setup_logger

logger = setup_logger()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
EMAIL_USER = os.getenv("EMAIL_USER", EMAIL_SENDER)  # Fallback to EMAIL_SENDER if not set


def send_email_with_attachment(subject, body, attachment_path):
    if not (EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECIPIENT and EMAIL_USER):
        logger.warning("Email credentials or recipient not set. Skipping email notification.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg.set_content(body)

    try:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)

        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"Email with attachment '{file_name}' sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
