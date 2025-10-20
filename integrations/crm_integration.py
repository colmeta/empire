"""
CRM Integration (HubSpot, Salesforce)
Cost: $0 (uses free API tiers)
Setup: Requires HUBSPOT_API_KEY in .env
"""

import requests
import os
from datetime import datetime

class HubSpotCRM:
    def __init__(self):
        """Initialize HubSpot CRM integration"""
        self.api_key = os.getenv('HUBSPOT_API_KEY')
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            self.enabled = True
            print("✅ HubSpot CRM integration enabled")
        else:
            self.enabled = False
            print("⚠️ HubSpot CRM integration disabled (missing API key)")
    
    def create_contact(self, name, email=None, phone=None, notes=None):
        """
        Create a contact in HubSpot
        
        Args:
            name: Full name
            email: Email address (optional)
            phone: Phone number (optional)
            notes: Additional notes (optional)
            
        Returns:
            str: Contact ID if successful, None otherwise
        """
        if not self.enabled:
            print("❌ HubSpot not enabled. Add HUBSPOT_API_KEY to .env")
            return None
        
        # Split name into first and last
        name_parts = name.split(' ', 1)
        firstname = name_parts[0] if len(name_parts) > 0 else ''
        lastname = name_parts[1] if len(name_parts) > 1 else ''
        
        # Build properties
        properties = {
            "firstname": firstname,
            "lastname": lastname,
            "hs_lead_status": "NEW",
            "lead_source": "Chatbot"
        }
        
        if email:
            properties["email"] = email
        if phone:
            properties["phone"] = phone
        if notes:
            properties["notes"] = notes
        
        payload = {"properties": properties}
        
        try:
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/contacts",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                contact_id = response.json()['id']
                print(f"✅ Contact created in HubSpot: {name} (ID: {contact_id})")
                return contact_id
            else:
                print(f"❌ HubSpot error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating contact: {e}")
            return None
    
    def create_deal(self, contact_id, deal_name, amount=0):
        """
        Create a deal/opportunity in HubSpot
        
        Args:
            contact_id: HubSpot contact ID
            deal_name: Name of the deal
            amount: Deal value in dollars
            
        Returns:
            str: Deal ID if successful, None otherwise
        """
        if not self.enabled:
            return None
        
        properties = {
            "dealname": deal_name,
            "amount": amount,
            "dealstage": "appointmentscheduled",
            "pipeline": "default",
            "lead_source": "Chatbot"
        }
        
        # Associate with contact
        associations = [{
            "to": {"id": contact_id},
            "types": [{
                "associationCategory": "HUBSPOT_DEFINED",
                "associationTypeId": 3
            }]
        }]
        
        payload = {
            "properties": properties,
            "associations": associations
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/deals",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                deal_id = response.json()['id']
                print(f"✅ Deal created in HubSpot (ID: {deal_id})")
                return deal_id
            else:
                print(f"❌ Error creating deal: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def add_note(self, contact_id, note_text):
        """
        Add a note to a contact
        
        Args:
            contact_id: HubSpot contact ID
            note_text: Note content
            
        Returns:
            bool: True if successful
        """
        if not self.enabled:
            return False
        
        payload = {
            "properties": {
                "hs_timestamp": datetime.now().isoformat(),
                "hs_note_body": note_text
            },
            "associations": [{
                "to": {"id": contact_id},
                "types": [{
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": 202
                }]
            }]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/notes",
                headers=self.headers,
                json=payload
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error adding note: {e}")
            return False


class SalesforceCRM:
    def __init__(self):
        """Initialize Salesforce CRM integration"""
        self.instance_url = os.getenv('SALESFORCE_INSTANCE_URL')
        self.access_token = os.getenv('SALESFORCE_ACCESS_TOKEN')
        
        if self.instance_url and self.access_token:
            self.enabled = True
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            print("✅ Salesforce CRM integration enabled")
        else:
            self.enabled = False
            print("⚠️ Salesforce CRM integration disabled (missing credentials)")
    
    def create_lead(self, first_name, last_name, email=None, phone=None, company=None):
        """
        Create a lead in Salesforce
        
        Args:
            first_name: First name
            last_name: Last name
            email: Email (optional)
            phone: Phone (optional)
            company: Company name (optional)
            
        Returns:
            str: Lead ID if successful
        """
        if not self.enabled:
            print("❌ Salesforce not enabled")
            return None
        
        payload = {
            "FirstName": first_name,
            "LastName": last_name,
            "LeadSource": "Chatbot",
            "Status": "New"
        }
        
        if email:
            payload["Email"] = email
        if phone:
            payload["Phone"] = phone
        if company:
            payload["Company"] = company
        else:
            payload["Company"] = "Unknown"  # Required field
        
        try:
            response = requests.post(
                f"{self.instance_url}/services/data/v58.0/sobjects/Lead",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                lead_id = response.json()['id']
                print(f"✅ Lead created in Salesforce: {first_name} {last_name}")
                return lead_id
            else:
                print(f"❌ Salesforce error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


# Unified CRM class (automatically detects which CRM to use)
class CRMIntegration:
    def __init__(self):
        """Initialize available CRM integrations"""
        self.hubspot = HubSpotCRM()
        self.salesforce = SalesforceCRM()
        
        # Determine which CRM is available
        if self.hubspot.enabled:
            self.active_crm = 'hubspot'
            self.enabled = True
        elif self.salesforce.enabled:
            self.active_crm = 'salesforce'
            self.enabled = True
        else:
            self.active_crm = None
            self.enabled = False
            print("⚠️ No CRM integration available")
    
    def capture_lead(self, lead_data):
        """
        Capture lead to whichever CRM is available
        
        Args:
            lead_data: dict with keys: name, email, phone, notes
            
        Returns:
            str: Lead/Contact ID if successful
        """
        if not self.enabled:
            print("❌ No CRM configured")
            return None
        
        if self.active_crm == 'hubspot':
            return self.hubspot.create_contact(
                name=lead_data.get('name', ''),
                email=lead_data.get('email'),
                phone=lead_data.get('phone'),
                notes=lead_data.get('notes')
            )
        elif self.active_crm == 'salesforce':
            name_parts = lead_data.get('name', '').split(' ', 1)
            return self.salesforce.create_lead(
                first_name=name_parts[0] if name_parts else '',
                last_name=name_parts[1] if len(name_parts) > 1 else '',
                email=lead_data.get('email'),
                phone=lead_data.get('phone'),
                company=lead_data.get('company')
            )
        
        return None


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    crm = CRMIntegration()
    if crm.enabled:
        print(f"\n✅ CRM Integration Active: {crm.active_crm.upper()}")
    else:
        print("\n⚠️ Add CRM credentials to .env:")
        print("For HubSpot: HUBSPOT_API_KEY=your_key")
        print("For Salesforce: SALESFORCE_INSTANCE_URL and SALESFORCE_ACCESS_TOKEN")
