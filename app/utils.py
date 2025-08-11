# app/utils.py
import random
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def role_required(*roles):
    """Decorator to restrict route access to specific user roles."""
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role.value not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("facility.list_facilities"))
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


def generate_otp(n=6):
    """Generate numeric OTP of n digits."""
    return ''.join([str(random.randint(0, 9)) for _ in range(n)])


def send_email_smtp(subject, to_email, html_body, text_body=None):
    """
    Sends email using SMTP settings in environment variables.
    Works with Gmail App Passwords.
    """
    smtp_host = os.getenv('EMAIL_HOST')
    smtp_port = int(os.getenv('EMAIL_PORT', 587))
    smtp_user = os.getenv('EMAIL_HOST_USER')
    smtp_pass = os.getenv('EMAIL_HOST_PASSWORD')
    use_tls = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')

    if not smtp_host or not smtp_user or not smtp_pass:
        raise RuntimeError("❌ SMTP configuration missing in environment variables")

    # Log for debugging
    print(f"📧 Sending email via {smtp_host}:{smtp_port} as {smtp_user} to {to_email}")

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    if text_body is None:
        text_body = html_body

    part1 = MIMEText(text_body, "plain")
    part2 = MIMEText(html_body, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False
