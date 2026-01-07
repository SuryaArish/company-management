#!/usr/bin/env python3
"""
Test script for Email Reminder API
Tests both manual and automatic email reminder functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.handlers import send_email_reminders
from app.services import firebase
from datetime import datetime, timedelta

async def test_email_reminders():
    """Test the email reminder functionality"""
    
    print("🧪 Testing Email Reminder API")
    print("=" * 50)
    
    try:
        # Test 1: Get users for reminder
        print("\n📋 Test 1: Fetching users with reminder settings...")
        users = await firebase.get_users_for_reminder()
        print(f"✅ Found {len(users)} users with reminder settings enabled")
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 User {i}:")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Days Before: {user.get('days_before', 'N/A')}")
            print(f"   Time of Day: {user.get('time_of_day', 'N/A')}")
            print(f"   Created At: {user.get('created_at', 'N/A')}")
            print(f"   CC Emails: {user.get('cc_emails', [])}")
        
        # Test 2: Manual email reminder trigger
        print(f"\n📧 Test 2: Manual email reminder trigger...")
        result = await send_email_reminders()
        print(f"✅ Manual trigger result: {result}")
        
        # Test 3: Test email sending function directly
        print(f"\n📬 Test 3: Testing email sending function...")
        if users:
            test_user = users[0]
            email_result = await firebase.send_reminder_email(
                test_user['email'],
                test_user.get('cc_emails', []),
                test_user['user_id']
            )
            print(f"✅ Direct email test result: {email_result}")
        else:
            print("⚠️ No users available for direct email test")
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

async def test_date_calculations():
    """Test date calculation logic"""
    
    print("\n🗓️ Testing Date Calculation Logic")
    print("=" * 40)
    
    # Test scenarios
    test_cases = [
        {
            "created_date": "2024-01-01T12:00:00Z",
            "days_before": 3,
            "expected_reminder": "2024-01-04"
        },
        {
            "created_date": "2024-01-15T08:30:00Z", 
            "days_before": 7,
            "expected_reminder": "2024-01-22"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📅 Test Case {i}:")
        print(f"   Created: {case['created_date']}")
        print(f"   Days Before: {case['days_before']}")
        
        # Parse date
        created_date = datetime.fromisoformat(case['created_date'].replace('Z', '+00:00')).date()
        reminder_date = created_date + timedelta(days=case['days_before'])
        
        print(f"   Calculated Reminder Date: {reminder_date}")
        print(f"   Expected: {case['expected_reminder']}")
        print(f"   ✅ Match: {str(reminder_date) == case['expected_reminder']}")

def test_time_logic():
    """Test time-based trigger logic"""
    
    print("\n⏰ Testing Time-Based Logic")
    print("=" * 30)
    
    current_time = "14:30"
    test_times = ["12:00", "14:30", "15:00", "09:00"]
    
    current_hour, current_minute = map(int, current_time.split(":"))
    current_minutes_total = current_hour * 60 + current_minute
    
    print(f"Current time: {current_time} ({current_minutes_total} minutes)")
    
    for reminder_time in test_times:
        reminder_hour, reminder_minute = map(int, reminder_time.split(":"))
        reminder_minutes_total = reminder_hour * 60 + reminder_minute
        
        should_send = current_minutes_total >= reminder_minutes_total
        print(f"Reminder time {reminder_time}: {'✅ SEND' if should_send else '⏳ WAIT'}")

if __name__ == "__main__":
    print("🚀 Starting Email Reminder Tests")
    
    # Run date calculation tests (synchronous)
    test_date_calculations()
    test_time_logic()
    
    # Run async tests
    asyncio.run(test_email_reminders())
    
    print("\n✅ All tests completed!")