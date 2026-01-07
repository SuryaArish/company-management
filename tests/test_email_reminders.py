import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestEmailReminders:
    
    def test_send_email_reminders_success(self):
        """Test successful email reminder processing"""
        # Mock users data with reminder due today
        today = datetime.utcnow().date()
        created_date = today - timedelta(days=4)  # Created 4 days ago, daysBefore=5, so reminder is today
        
        mock_users = [
            {
                "user_id": "user123",
                "email": "test@example.com",
                "created_at": created_date.strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 5,
                "cc_emails": ["cc1@example.com", "cc2@example.com"]
            }
        ]
        
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            with patch('app.services.firebase.send_reminder_email', new_callable=AsyncMock) as mock_send_email:
                mock_get_users.return_value = mock_users
                mock_send_email.return_value = True
                
                response = client.post("/send_email_reminders")
                
                assert response.status_code == 200
                assert "Email reminders processed. Sent 1 emails." in response.json()["message"]
                mock_send_email.assert_called_once_with("test@example.com", ["cc1@example.com", "cc2@example.com"], "user123")

    def test_send_email_reminders_no_users(self):
        """Test when no users need reminders"""
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            mock_get_users.return_value = []
            
            response = client.post("/send_email_reminders")
            
            assert response.status_code == 200
            assert "Email reminders processed. Sent 0 emails." in response.json()["message"]

    def test_send_email_reminders_wrong_date(self):
        """Test when reminder date doesn't match today"""
        today = datetime.utcnow().date()
        created_date = today - timedelta(days=2)  # Created 2 days ago, daysBefore=5, so reminder is in 2 days
        
        mock_users = [
            {
                "user_id": "user123",
                "email": "test@example.com",
                "created_at": created_date.strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 5,
                "cc_emails": []
            }
        ]
        
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            with patch('app.services.firebase.send_reminder_email', new_callable=AsyncMock) as mock_send_email:
                mock_get_users.return_value = mock_users
                
                response = client.post("/send_email_reminders")
                
                assert response.status_code == 200
                assert "Email reminders processed. Sent 0 emails." in response.json()["message"]
                mock_send_email.assert_not_called()

    def test_send_email_reminders_multiple_users(self):
        """Test with multiple users, some due for reminders"""
        today = datetime.utcnow().date()
        
        mock_users = [
            {
                "user_id": "user1",
                "email": "user1@example.com",
                "created_at": (today - timedelta(days=4)).strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 5,
                "cc_emails": ["cc1@example.com"]
            },
            {
                "user_id": "user2",
                "email": "user2@example.com",
                "created_at": (today - timedelta(days=2)).strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 5,
                "cc_emails": []
            },
            {
                "user_id": "user3",
                "email": "user3@example.com",
                "created_at": (today - timedelta(days=6)).strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 7,
                "cc_emails": ["cc3@example.com"]
            }
        ]
        
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            with patch('app.services.firebase.send_reminder_email', new_callable=AsyncMock) as mock_send_email:
                mock_get_users.return_value = mock_users
                mock_send_email.return_value = True
                
                response = client.post("/send_email_reminders")
                
                assert response.status_code == 200
                assert "Email reminders processed. Sent 2 emails." in response.json()["message"]
                assert mock_send_email.call_count == 2

    def test_send_email_reminders_zero_days_before(self):
        """Test users with daysBefore = 0 (should be ignored)"""
        today = datetime.utcnow().date()
        
        mock_users = [
            {
                "user_id": "user123",
                "email": "test@example.com",
                "created_at": today.strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 0,
                "cc_emails": []
            }
        ]
        
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            with patch('app.services.firebase.send_reminder_email', new_callable=AsyncMock) as mock_send_email:
                mock_get_users.return_value = mock_users
                
                response = client.post("/send_email_reminders")
                
                assert response.status_code == 200
                assert "Email reminders processed. Sent 0 emails." in response.json()["message"]
                mock_send_email.assert_not_called()

    def test_send_email_reminders_email_failure(self):
        """Test when email sending fails"""
        today = datetime.utcnow().date()
        created_date = today - timedelta(days=4)
        
        mock_users = [
            {
                "user_id": "user123",
                "email": "test@example.com",
                "created_at": created_date.strftime("%Y-%m-%dT00:00:00Z"),
                "days_before": 5,
                "cc_emails": []
            }
        ]
        
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            with patch('app.services.firebase.send_reminder_email', new_callable=AsyncMock) as mock_send_email:
                mock_get_users.return_value = mock_users
                mock_send_email.return_value = False
                
                response = client.post("/send_email_reminders")
                
                assert response.status_code == 200
                assert "Email reminders processed. Sent 0 emails." in response.json()["message"]

    def test_send_email_reminders_database_error(self):
        """Test when database query fails"""
        with patch('app.services.firebase.get_users_for_reminder', new_callable=AsyncMock) as mock_get_users:
            mock_get_users.side_effect = Exception("Database connection failed")
            
            response = client.post("/send_email_reminders")
            
            assert response.status_code == 500
            assert "Failed to process email reminders" in response.json()["detail"]

    def test_reminder_date_calculation(self):
        """Test the reminder date calculation logic"""
        # Test case: created on 2025-01-20, daysBefore=5, should send on 2025-01-24
        created_date = datetime(2025, 1, 20).date()
        days_before = 5
        expected_reminder_date = datetime(2025, 1, 24).date()
        
        calculated_reminder_date = created_date + timedelta(days=days_before - 1)
        
        assert calculated_reminder_date == expected_reminder_date

    def test_reminder_date_calculation_edge_cases(self):
        """Test edge cases for reminder date calculation"""
        # Test case: daysBefore=1, should send on same day
        created_date = datetime(2025, 1, 20).date()
        days_before = 1
        expected_reminder_date = datetime(2025, 1, 20).date()
        
        calculated_reminder_date = created_date + timedelta(days=days_before - 1)
        
        assert calculated_reminder_date == expected_reminder_date
        
        # Test case: daysBefore=10
        days_before = 10
        expected_reminder_date = datetime(2025, 1, 29).date()
        
        calculated_reminder_date = created_date + timedelta(days=days_before - 1)
        
        assert calculated_reminder_date == expected_reminder_date

if __name__ == "__main__":
    pytest.main([__file__, "-v"])