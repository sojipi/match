"""
Email notification service for sending notifications via email.
"""
from typing import Optional, Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
from jinja2 import Template
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        self.enabled = settings.EMAIL_ENABLED
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email disabled. Would have sent to {to_email}: {subject}")
            return True
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            
            if self.smtp_port == 465:
                # Use SSL
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, message.as_string())
            else:
                # Use STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls(context=context)
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_match_notification(
        self,
        to_email: str,
        user_name: str,
        match_name: str,
        match_photo_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> bool:
        """Send new match notification email."""
        subject = f"New Match with {match_name}! 💕"
        
        html_content = self._render_match_email(
            user_name=user_name,
            match_name=match_name,
            match_photo_url=match_photo_url,
            action_url=action_url
        )
        
        text_content = f"""
Hi {user_name},

You have a new match with {match_name}!

Visit {action_url or settings.FRONTEND_URL} to start chatting.

Best regards,
The AI Matchmaker Team
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_mutual_match_notification(
        self,
        to_email: str,
        user_name: str,
        match_name: str,
        match_photo_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> bool:
        """Send mutual match notification email."""
        subject = f"It's a Match! You and {match_name} liked each other! 🎉"
        
        html_content = self._render_mutual_match_email(
            user_name=user_name,
            match_name=match_name,
            match_photo_url=match_photo_url,
            action_url=action_url
        )
        
        text_content = f"""
Hi {user_name},

Congratulations! You and {match_name} liked each other!

Watch your AI avatars interact in real-time: {action_url or settings.FRONTEND_URL}

Best regards,
The AI Matchmaker Team
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_message_notification(
        self,
        to_email: str,
        user_name: str,
        sender_name: str,
        message_preview: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send new message notification email."""
        subject = f"New message from {sender_name}"
        
        html_content = self._render_message_email(
            user_name=user_name,
            sender_name=sender_name,
            message_preview=message_preview,
            action_url=action_url
        )
        
        text_content = f"""
Hi {user_name},

You have a new message from {sender_name}:

"{message_preview}"

Reply at: {action_url or settings.FRONTEND_URL}

Best regards,
The AI Matchmaker Team
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_compatibility_report_notification(
        self,
        to_email: str,
        user_name: str,
        match_name: str,
        compatibility_score: float,
        action_url: Optional[str] = None
    ) -> bool:
        """Send compatibility report ready notification email."""
        subject = f"Your Compatibility Report with {match_name} is Ready!"
        
        html_content = self._render_compatibility_report_email(
            user_name=user_name,
            match_name=match_name,
            compatibility_score=compatibility_score,
            action_url=action_url
        )
        
        text_content = f"""
Hi {user_name},

Your compatibility report with {match_name} is ready!

Compatibility Score: {int(compatibility_score * 100)}%

View your detailed report: {action_url or settings.FRONTEND_URL}

Best regards,
The AI Matchmaker Team
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    def _render_match_email(
        self,
        user_name: str,
        match_name: str,
        match_photo_url: Optional[str],
        action_url: Optional[str]
    ) -> str:
        """Render match notification email template."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .match-card { background: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .match-photo { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto 15px; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💕 New Match!</h1>
        </div>
        <div class="content">
            <p>Hi {{ user_name }},</p>
            <p>Great news! You have a new match!</p>
            
            <div class="match-card">
                {% if match_photo_url %}
                <img src="{{ match_photo_url }}" alt="{{ match_name }}" class="match-photo">
                {% endif %}
                <h2>{{ match_name }}</h2>
                <p>Start a conversation and see where it goes!</p>
            </div>
            
            {% if action_url %}
            <div style="text-align: center;">
                <a href="{{ action_url }}" class="button">View Match</a>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>You're receiving this email because you have notifications enabled.</p>
                <p>© 2026 AI Matchmaker. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
        """)
        
        return template.render(
            user_name=user_name,
            match_name=match_name,
            match_photo_url=match_photo_url,
            action_url=action_url
        )
    
    def _render_mutual_match_email(
        self,
        user_name: str,
        match_name: str,
        match_photo_url: Optional[str],
        action_url: Optional[str]
    ) -> str:
        """Render mutual match notification email template."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .match-card { background: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .match-photo { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto 15px; }
        .button { display: inline-block; background: #f5576c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .highlight { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 It's a Match!</h1>
        </div>
        <div class="content">
            <p>Hi {{ user_name }},</p>
            <p><strong>Congratulations!</strong> You and {{ match_name }} liked each other!</p>
            
            <div class="match-card">
                {% if match_photo_url %}
                <img src="{{ match_photo_url }}" alt="{{ match_name }}" class="match-photo">
                {% endif %}
                <h2>{{ match_name }}</h2>
            </div>
            
            <div class="highlight">
                <p><strong>What's Next?</strong></p>
                <p>Watch your AI avatars interact in real-time and see how compatible you are!</p>
            </div>
            
            {% if action_url %}
            <div style="text-align: center;">
                <a href="{{ action_url }}" class="button">Start Live Matching</a>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>You're receiving this email because you have notifications enabled.</p>
                <p>© 2026 AI Matchmaker. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
        """)
        
        return template.render(
            user_name=user_name,
            match_name=match_name,
            match_photo_url=match_photo_url,
            action_url=action_url
        )
    
    def _render_message_email(
        self,
        user_name: str,
        sender_name: str,
        message_preview: str,
        action_url: Optional[str]
    ) -> str:
        """Render message notification email template."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .message-card { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #667eea; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 New Message</h1>
        </div>
        <div class="content">
            <p>Hi {{ user_name }},</p>
            <p>You have a new message from <strong>{{ sender_name }}</strong>:</p>
            
            <div class="message-card">
                <p>"{{ message_preview }}"</p>
            </div>
            
            {% if action_url %}
            <div style="text-align: center;">
                <a href="{{ action_url }}" class="button">Reply Now</a>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>You're receiving this email because you have message notifications enabled.</p>
                <p>© 2026 AI Matchmaker. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
        """)
        
        return template.render(
            user_name=user_name,
            sender_name=sender_name,
            message_preview=message_preview,
            action_url=action_url
        )
    
    def _render_compatibility_report_email(
        self,
        user_name: str,
        match_name: str,
        compatibility_score: float,
        action_url: Optional[str]
    ) -> str:
        """Render compatibility report notification email template."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .score-card { background: white; padding: 30px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .score { font-size: 48px; font-weight: bold; color: #667eea; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Compatibility Report Ready</h1>
        </div>
        <div class="content">
            <p>Hi {{ user_name }},</p>
            <p>Your compatibility report with <strong>{{ match_name }}</strong> is ready!</p>
            
            <div class="score-card">
                <p>Compatibility Score</p>
                <div class="score">{{ score_percentage }}%</div>
                <p>View your detailed analysis to learn more about your compatibility.</p>
            </div>
            
            {% if action_url %}
            <div style="text-align: center;">
                <a href="{{ action_url }}" class="button">View Full Report</a>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>You're receiving this email because you have report notifications enabled.</p>
                <p>© 2026 AI Matchmaker. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
        """)
        
        return template.render(
            user_name=user_name,
            match_name=match_name,
            score_percentage=int(compatibility_score * 100),
            action_url=action_url
        )


# Global email service instance
email_service = EmailService()
