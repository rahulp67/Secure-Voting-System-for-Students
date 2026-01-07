"""
Email OTP Service
Sends OTP codes via SMTP email.

Configure your SMTP settings in config.py before using.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


def send_otp_email(to_email: str, otp_code: str, student_name: str) -> tuple[bool, str]:
    """
    Send OTP code to student's email.
    
    Args:
        to_email: Student's email address
        otp_code: 6-digit OTP code
        student_name: Student's name for personalization
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🔐 Your Voting OTP: {otp_code}'
        msg['From'] = f"Voting System <{Config.SMTP_USER}>"
        msg['To'] = to_email
        
        # Plain text version
        text_content = f"""
Hello {student_name},

Your one-time password (OTP) for the Student Voting System is:

    {otp_code}

This code will expire in 5 minutes.

If you did not request this code, please ignore this email.

- Student Voting System
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f0f23; color: #ffffff; padding: 20px; }}
        .container {{ max-width: 500px; margin: 0 auto; background: rgba(30, 30, 60, 0.9); border-radius: 16px; padding: 40px; border: 1px solid rgba(255,255,255,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ font-size: 48px; margin-bottom: 10px; }}
        h1 {{ color: #818cf8; margin: 0; font-size: 24px; }}
        .otp-box {{ background: linear-gradient(135deg, #6366f1, #4f46e5); padding: 20px; border-radius: 12px; text-align: center; margin: 30px 0; }}
        .otp-code {{ font-size: 36px; font-weight: bold; letter-spacing: 8px; color: white; }}
        .info {{ color: rgba(255,255,255,0.7); font-size: 14px; text-align: center; }}
        .warning {{ color: #f59e0b; font-size: 12px; margin-top: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🗳️</div>
            <h1>Student Voting System</h1>
        </div>
        <p>Hello <strong>{student_name}</strong>,</p>
        <p>Your one-time password (OTP) is:</p>
        <div class="otp-box">
            <div class="otp-code">{otp_code}</div>
        </div>
        <p class="info">This code will expire in <strong>5 minutes</strong>.</p>
        <p class="warning">⚠️ If you did not request this code, please ignore this email.</p>
    </div>
</body>
</html>
"""
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True, "OTP sent successfully!"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Check SMTP credentials."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def send_test_email(to_email: str) -> tuple[bool, str]:
    """Send a test email to verify SMTP configuration."""
    try:
        msg = MIMEText("This is a test email from the Student Voting System. SMTP is configured correctly!")
        msg['Subject'] = '✅ SMTP Test - Voting System'
        msg['From'] = Config.SMTP_USER
        msg['To'] = to_email
        
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True, "Test email sent successfully!"
    except Exception as e:
        return False, f"Failed: {str(e)}"
