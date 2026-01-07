import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class GmailAPIService:
    def __init__(self):
        self.client_id = os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET") 
        self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
        self.sender_email = os.getenv("GMAIL_SENDER_EMAIL")
        self._access_token = None
    
    async def get_access_token(self):
        """Get fresh access token using refresh token"""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._access_token = data["access_token"]
                    return self._access_token
                else:
                    print(f"❌ Failed to get access token: {response.text}")
                    return None
        except Exception as e:
            print(f"❌ Error getting access token: {e}")
            return None
    
    async def send_email(self, to_email: str, cc_emails: list, subject: str, body: str):
        """Send email using Gmail API"""
        try:
            # Get access token
            access_token = await self.get_access_token()
            if not access_token:
                print("❌ No access token available")
                return False
            
            # Create email message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = to_email
            if cc_emails:
                message['Cc'] = ', '.join(cc_emails)
            message['Subject'] = subject
            
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://gmail.googleapis.com/gmail/v1/users/{self.sender_email}/messages/send",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={"raw": raw_message}
                )
                
                if response.status_code == 200:
                    print(f"✅ Email sent successfully via Gmail API to {to_email}")
                    if cc_emails:
                        print(f"✅ CC sent to: {', '.join(cc_emails)}")
                    return True
                else:
                    print(f"❌ Failed to send email: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error sending email via Gmail API: {e}")
            return False

# Global instance
gmail_service = GmailAPIService()