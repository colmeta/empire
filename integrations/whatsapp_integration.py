"""
WhatsApp Integration using Twilio
Cost: $0.005 per outgoing message
Setup: Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER in .env
"""

from twilio.rest import Client
import os
from datetime import datetime

class WhatsAppIntegration:
    def __init__(self):
        """Initialize Twilio WhatsApp client"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        # Only initialize if credentials exist
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
            print("✅ WhatsApp integration enabled")
        else:
            self.client = None
            self.enabled = False
            print("⚠️ WhatsApp integration disabled (missing Twilio credentials)")
    
    def send_message(self, to_phone, message_text):
        """
        Send a WhatsApp message
        
        Args:
            to_phone: Phone number with country code (e.g., '+13055551234')
            message_text: Message content
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            print("❌ WhatsApp not enabled. Add Twilio credentials to .env")
            return False
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            message = self.client.messages.create(
                body=message_text,
                from_=self.whatsapp_number,
                to=to_phone
            )
            
            print(f"✅ WhatsApp message sent: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending WhatsApp message: {e}")
            return False
    
    def send_appointment_reminder(self, patient_name, appointment_time, phone, business_name):
        """
        Send appointment reminder via WhatsApp
        
        Args:
            patient_name: Patient/customer name
            appointment_time: Appointment datetime string
            phone: Phone number
            business_name: Business name
        """
        message = f"""
Hi {patient_name}! 👋

This is a reminder about your appointment at {business_name}:

📅 {appointment_time}

Reply CONFIRM to confirm or RESCHEDULE if you need to change.

See you soon!
        """.strip()
        
        return self.send_message(phone, message)
    
    def send_welcome_message(self, phone, business_name):
        """Send welcome message to new WhatsApp contacts"""
        message = f"""
Welcome to {business_name}! 👋

I'm your AI assistant. I can help you with:
• Business hours & location
• Services & pricing
• Booking appointments
• Answering questions

How can I help you today?
        """.strip()
        
        return self.send_message(phone, message)


# Usage example (will be called from main app):
def process_incoming_whatsapp_message(from_number, message_body, chatbot_response_function):
    """
    Process incoming WhatsApp message and send AI response
    
    Args:
        from_number: WhatsApp number that sent message
        message_body: Message text
        chatbot_response_function: Function that generates AI response
        
    Returns:
        bool: True if processed successfully
    """
    whatsapp = WhatsAppIntegration()
    
    if not whatsapp.enabled:
        return False
    
    # Create session ID from phone number
    session_id = from_number.replace('whatsapp:', '').replace('+', '')
    
    # Get AI response
    ai_response = chatbot_response_function(session_id, message_body)
    
    # Send reply via WhatsApp
    return whatsapp.send_message(from_number, ai_response)


# Test function (only run if credentials exist)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    whatsapp = WhatsAppIntegration()
    if whatsapp.enabled:
        print("\n✅ WhatsApp Integration Test")
        print("Credentials found - ready to send messages!")
    else:
        print("\n⚠️ WhatsApp Integration Test")
        print("Add these to your .env file:")
        print("TWILIO_ACCOUNT_SID=your_account_sid")
        print("TWILIO_AUTH_TOKEN=your_auth_token")
        print("TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886")
