"""
Calendar Integration (Calendly, Google Calendar)
Cost: $0 (uses free tiers)
Setup: Requires CALENDLY_API_KEY in .env (optional)
"""

import requests
import os
from datetime import datetime

class CalendlyIntegration:
    def __init__(self):
        """Initialize Calendly integration"""
        self.api_key = os.getenv('CALENDLY_API_KEY')
        self.base_url = "https://api.calendly.com"
        self.calendly_username = os.getenv('CALENDLY_USERNAME', '')
        
        if self.api_key:
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            self.enabled = True
            print("✅ Calendly API integration enabled")
        else:
            self.headers = None
            self.enabled = False
            print("⚠️ Calendly API disabled (using direct links instead)")
    
    def get_booking_link(self, event_type="30min"):
        """
        Get Calendly booking link
        
        Args:
            event_type: Event type slug (e.g., "30min", "consultation")
            
        Returns:
            str: Booking URL
        """
        if self.calendly_username:
            return f"https://calendly.com/{self.calendly_username}/{event_type}"
        else:
            return "https://calendly.com/your-username/30min"
    
    def get_widget_code(self, event_type="30min"):
        """
        Get embeddable Calendly widget HTML code
        
        Args:
            event_type: Event type slug
            
        Returns:
            str: HTML code for embedding
        """
        booking_url = self.get_booking_link(event_type)
        
        return f'''
<!-- Calendly inline widget begin -->
<div class="calendly-inline-widget" 
     data-url="{booking_url}" 
     style="min-width:320px;height:700px;">
</div>
<script type="text/javascript" 
        src="https://assets.calendly.com/assets/external/widget.js" 
        async>
</script>
<!-- Calendly inline widget end -->
        '''
    
    def get_popup_code(self, event_type="30min"):
        """
        Get Calendly popup button code
        
        Returns:
            str: HTML code for popup button
        """
        booking_url = self.get_booking_link(event_type)
        
        return f'''
<!-- Calendly link widget begin -->
<link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet">
<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript" async></script>
<a href="" onclick="Calendly.initPopupWidget({{url: '{booking_url}'}});return false;">
    Schedule Appointment
</a>
<!-- Calendly link widget end -->
        '''
    
    def format_booking_message(self, business_name, event_type="30min"):
        """
        Generate chatbot message with booking link
        
        Args:
            business_name: Business name
            event_type: Event type
            
        Returns:
            str: Formatted message
        """
        booking_link = self.get_booking_link(event_type)
        
        return f"""
Great! I'd be happy to help you schedule an appointment with {business_name}.

📅 Click here to choose a time that works for you:
{booking_link}

You'll be able to see all available time slots and book instantly. The system will send you automatic reminders before your appointment.

Is there anything else you'd like to know?
        """.strip()


class GoogleCalendarIntegration:
    def __init__(self):
        """Initialize Google Calendar integration"""
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('GOOGLE_TOKEN_FILE', 'token.json')
        
        # Check if files exist
        if os.path.exists(self.token_file):
            self.enabled = True
            print("✅ Google Calendar integration enabled")
        else:
            self.enabled = False
            print("⚠️ Google Calendar disabled (run setup first)")
    
    def create_event(self, summary, start_time, end_time, attendee_email=None, description=""):
        """
        Create event in Google Calendar
        
        Args:
            summary: Event title
            start_time: Start datetime (ISO format)
            end_time: End datetime (ISO format)
            attendee_email: Guest email (optional)
            description: Event description
            
        Returns:
            str: Event ID if successful
        """
        if not self.enabled:
            print("❌ Google Calendar not set up")
            return None
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            creds = Credentials.from_authorized_user_file(self.token_file)
            service = build('calendar', 'v3', credentials=creds)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            result = service.events().insert(calendarId='primary', body=event).execute()
            print(f"✅ Google Calendar event created: {result.get('id')}")
            return result.get('id')
            
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def get_availability(self, date):
        """
        Get available time slots for a date
        
        Args:
            date: Date to check (YYYY-MM-DD)
            
        Returns:
            list: Available time slots
        """
        if not self.enabled:
            return []
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            creds = Credentials.from_authorized_user_file(self.token_file)
            service = build('calendar', 'v3', credentials=creds)
            
            # Get events for the day
            time_min = f"{date}T00:00:00Z"
            time_max = f"{date}T23:59:59Z"
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Return busy times (you'd calculate free times from this)
            busy_times = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                busy_times.append({'start': start, 'end': end})
            
            return busy_times
            
        except Exception as e:
            print(f"❌ Error getting availability: {e}")
            return []


# Unified Calendar class
class CalendarIntegration:
    def __init__(self):
        """Initialize available calendar integrations"""
        self.calendly = CalendlyIntegration()
        self.google = GoogleCalendarIntegration()
        
        # Determine which calendar is available
        if self.calendly.calendly_username:
            self.active_calendar = 'calendly'
            self.enabled = True
        elif self.google.enabled:
            self.active_calendar = 'google'
            self.enabled = True
        else:
            self.active_calendar = 'calendly'  # Default to Calendly links
            self.enabled = True  # Can always use Calendly links
            print("⚠️ Using Calendly direct links (no API)")
    
    def get_booking_message(self, business_name):
        """
        Get booking message for chatbot
        
        Args:
            business_name: Business name
            
        Returns:
            str: Message with booking information
        """
        if self.active_calendar == 'calendly':
            return self.calendly.format_booking_message(business_name)
        elif self.active_calendar == 'google':
            return """
I can help you schedule an appointment! Please provide:
• Your preferred date
• Your preferred time
• Your email address

And I'll check availability for you.
            """.strip()
        
        return "Please call us to schedule an appointment."
    
    def create_appointment(self, appointment_data):
        """
        Create appointment in available calendar system
        
        Args:
            appointment_data: dict with appointment details
            
        Returns:
            str: Appointment ID or booking link
        """
        if self.active_calendar == 'google':
            return self.google.create_event(
                summary=appointment_data.get('title', 'Appointment'),
                start_time=appointment_data.get('start_time'),
                end_time=appointment_data.get('end_time'),
                attendee_email=appointment_data.get('email'),
                description=appointment_data.get('notes', '')
            )
        else:
            # Return Calendly link
            return self.calendly.get_booking_link()


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    calendar = CalendarIntegration()
    print(f"\n✅ Calendar Integration Active: {calendar.active_calendar.upper()}")
    
    if calendar.active_calendar == 'calendly':
        print("\nTo use Calendly:")
        print("1. Create account at calendly.com")
        print("2. Add to .env: CALENDLY_USERNAME=your-username")
        print("3. (Optional) Add API key: CALENDLY_API_KEY=your_key")
    
    print("\n📅 Sample booking message:")
    print(calendar.get_booking_message("Sunshine Dental"))
