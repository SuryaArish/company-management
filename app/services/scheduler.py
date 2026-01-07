import asyncio
import schedule
import time
from datetime import datetime
from app.api.handlers import send_email_reminders
import threading

class EmailReminderScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            print("📅 Scheduler already running")
            return
        
        self.running = True
        
        # Schedule email reminders to run every hour
        schedule.every().hour.do(self._run_email_reminders)
        
        # Also schedule specific times for more precise control
        schedule.every().day.at("09:00").do(self._run_email_reminders)
        schedule.every().day.at("12:00").do(self._run_email_reminders)
        schedule.every().day.at("15:00").do(self._run_email_reminders)
        schedule.every().day.at("18:00").do(self._run_email_reminders)
        
        # Start scheduler in background thread
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        
        print("✅ Email reminder scheduler started")
        print("📅 Scheduled to run: Every hour + at 09:00, 12:00, 15:00, 18:00 UTC")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        schedule.clear()
        print("🛑 Email reminder scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop running in background thread"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(60)
    
    def _run_email_reminders(self):
        """Wrapper to run async email reminders in sync context"""
        try:
            print(f"🔔 Scheduler triggered email reminders at {datetime.utcnow()}")
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the email reminders
            result = loop.run_until_complete(send_email_reminders())
            
            print(f"✅ Scheduled email reminders completed: {result}")
            
        except Exception as e:
            print(f"❌ Error in scheduled email reminders: {e}")
        finally:
            try:
                loop.close()
            except:
                pass

# Global scheduler instance
email_scheduler = EmailReminderScheduler()

def start_email_scheduler():
    """Start the email reminder scheduler"""
    email_scheduler.start_scheduler()

def stop_email_scheduler():
    """Stop the email reminder scheduler"""
    email_scheduler.stop_scheduler()