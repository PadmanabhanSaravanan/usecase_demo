# monitor/emailer.py
import smtplib
import ssl
from email.message import EmailMessage
from typing import List

def send_email(
    smtp_host: str,
    smtp_port: int,
    use_tls: bool,
    username: str,
    password: str,
    from_email: str,
    to_emails: List[str],
    subject: str,
    body: str,
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)
    msg.set_content(body)

    if use_tls:
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(username, password)
            server.send_message(msg)
