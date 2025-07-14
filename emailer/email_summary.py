
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from configparser import ConfigParser
import os

def send_email_with_summary(to_address, bullish_results, full_excel_path=None):
    config = ConfigParser()
    config.read("config/email.ini")

    sender_email = config.get("EMAIL", "sender")
    sender_name = config.get("EMAIL", "sender_name")
    password = config.get("EMAIL", "password")
    smtp_server = config.get("EMAIL", "smtp_server")
    smtp_port = config.getint("EMAIL", "smtp_port")

    subject = "📈 Bullish Screener Summary"
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to_address

    if bullish_results:
        body = "🟢 Bullish signals detected:"
        for row in bullish_results:
            body += f"- {row['symbol']}: ${row['price']} ({row['company_name']})\n"
    else:
        body = "⚠️ No bullish signals detected in the current run."

    if full_excel_path and Path(full_excel_path).exists():
        with open(full_excel_path, "rb") as f:
            file_data = f.read()
            filename = Path(full_excel_path).name
            msg.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)
            body += f"\n\nFull results attached: {filename}"

    msg.set_content(body)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, password)
        server.send_message(msg)
