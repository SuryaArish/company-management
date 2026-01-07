#!/usr/bin/env python3
"""
Simple test runner for email reminder API
Run this script to test the email reminder functionality
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoint():
    """Test the actual API endpoint"""
    print("🧪 Testing Email Reminder API Endpoint")
    print("=" * 50)
    
    try:
        # Test the API endpoint
        response = requests.post("http://localhost:8080/send_email_reminders")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API endpoint is working!")
        else:
            print("❌ API endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on localhost:8080")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_unit_tests():
    """Run the unit tests"""
    print("\n🧪 Running Unit Tests")
    print("=" * 50)
    
    try:
        import pytest
        # Run the tests
        exit_code = pytest.main([
            "tests/test_email_reminders.py", 
            "-v", 
            "--tb=short"
        ])
        
        if exit_code == 0:
            print("✅ All unit tests passed!")
        else:
            print("❌ Some unit tests failed!")
            
    except ImportError:
        print("❌ pytest not installed. Install with: pip install pytest")
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def show_test_scenarios():
    """Show test scenarios and expected results"""
    print("\n📋 Test Scenarios")
    print("=" * 50)
    
    today = datetime.now().date()
    
    scenarios = [
        {
            "name": "User should receive reminder today",
            "created_date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "days_before": 5,
            "reminder_date": today.strftime("%Y-%m-%d"),
            "should_send": True
        },
        {
            "name": "User should NOT receive reminder (too early)",
            "created_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "days_before": 5,
            "reminder_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "should_send": False
        },
        {
            "name": "User with daysBefore=1 (same day reminder)",
            "created_date": today.strftime("%Y-%m-%d"),
            "days_before": 1,
            "reminder_date": today.strftime("%Y-%m-%d"),
            "should_send": True
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Created: {scenario['created_date']}")
        print(f"   Days Before: {scenario['days_before']}")
        print(f"   Reminder Date: {scenario['reminder_date']}")
        print(f"   Should Send Today: {'✅ YES' if scenario['should_send'] else '❌ NO'}")

def main():
    """Main test runner"""
    print("🚀 Email Reminder API Test Suite")
    print("=" * 50)
    
    # Show test scenarios
    show_test_scenarios()
    
    # Run unit tests
    run_unit_tests()
    
    # Test actual API endpoint
    test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("📝 Test Summary:")
    print("1. Unit tests verify the logic with mocked data")
    print("2. API test calls the actual endpoint")
    print("3. Check console output for email logs")
    print("\n💡 To see actual emails being sent:")
    print("   - Add test users to Firebase with appropriate dates")
    print("   - Run the API on the calculated reminder dates")

if __name__ == "__main__":
    main()