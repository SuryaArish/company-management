#!/usr/bin/env python3
"""
OAuth Helper Script - Get Gmail API Refresh Token
Run this once to get the refresh token for Gmail API
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import httpx
import urllib.parse
import webbrowser

# Load environment variables
load_dotenv("config/.env")

CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/oauth/callback"

def get_refresh_token():
    """Get refresh token for Gmail API"""
    
    print("🔐 Gmail API OAuth Setup")
    print("=" * 40)
    
    # Step 1: Generate authorization URL
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        "scope=https://www.googleapis.com/auth/gmail.send&"
        "response_type=code&"
        "access_type=offline&"
        "prompt=consent"
    )
    
    print(f"📋 Step 1: Open this URL in your browser:")
    print(f"🔗 {auth_url}")
    print()
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened automatically")
    except:
        print("⚠️ Please copy and paste the URL manually")
    
    print()
    print("📋 Step 2: After authorization, you'll be redirected to:")
    print(f"   {REDIRECT_URI}?code=AUTHORIZATION_CODE")
    print()
    print("📋 Step 3: Copy the 'code' parameter from the URL")
    
    # Get authorization code from user
    auth_code = input("\n🔑 Paste the authorization code here: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return None
    
    # Step 2: Exchange code for tokens
    print("\n🔄 Exchanging code for tokens...")
    
    try:
        with httpx.Client() as client:
            response = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": auth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI
                }
            )
            
            if response.status_code == 200:
                tokens = response.json()
                refresh_token = tokens.get("refresh_token")
                
                if refresh_token:
                    print("✅ Success! Got refresh token:")
                    print(f"🔑 {refresh_token}")
                    print()
                    print("📝 Add this to your .env file:")
                    print(f"GMAIL_REFRESH_TOKEN={refresh_token}")
                    return refresh_token
                else:
                    print("❌ No refresh token in response")
                    print(f"Response: {tokens}")
                    return None
            else:
                print(f"❌ Failed to get tokens: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Missing CLIENT_ID or CLIENT_SECRET in .env file")
        sys.exit(1)
    
    refresh_token = get_refresh_token()
    
    if refresh_token:
        print("\n🎉 Setup complete!")
        print("📧 You can now send emails via Gmail API")
    else:
        print("\n❌ Setup failed. Please try again.")