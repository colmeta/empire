"""
Integration modules for chatbot
Import these in your main chatbot_app.py file
"""

from .whatsapp_integration import WhatsAppIntegration, process_incoming_whatsapp_message
from .crm_integration import CRMIntegration
from .calendar_integration import CalendarIntegration

__all__ = [
    'WhatsAppIntegration',
    'process_incoming_whatsapp_message',
    'CRMIntegration',
    'CalendarIntegration'
]
