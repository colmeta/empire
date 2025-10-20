# CHATBOT EMPIRE BUILDER - Complete Free Platform Implementation
# Cost: $0-15/month | Sell for: $1,200-2,500 setup + $200-500/month
# Profit Margin: 10,000%+ on setup, 90%+ on monthly

"""
DEPLOYMENT OPTIONS (ALL FREE):
1. Render.com - Free tier (perfect for most clients)
2. Railway.app - $5/month (if need more resources)
3. Vercel - Free (for frontend hosting)

DATABASE OPTIONS (ALL FREE):
1. Supabase - Free tier with PostgreSQL + Vector DB
2. Firebase - Free tier
3. MongoDB Atlas - Free tier

AI OPTIONS:
1. OpenAI API - $0.002 per conversation ($2-10/month typical)
2. Claude API - Similar pricing
"""

from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# =============================================================================
# CONFIGURATION - CUSTOMIZE FOR EACH CLIENT
# =============================================================================

BUSINESS_CONFIG = {
    "name": "Sunshine Dental Clinic",
    "industry": "Healthcare",
    "description": """
    We are a family dental practice in Miami, FL specializing in preventive 
    and cosmetic dentistry.
    
    Services & Pricing:
    - Teeth Cleaning: $120
    - Teeth Whitening: $350
    - Fillings: $180-250
    - Root Canals: $800-1200
    - Dental Implants: $2,500-4,000
    - Emergency Services: Available same-day
    
    Hours:
    - Monday-Friday: 8am - 6pm
    - Saturday: 9am - 2pm
    - Sunday: Closed
    - Emergency: 24/7 on-call
    
    Location:
    - 123 Main Street, Miami, FL 33101
    - Phone: (305) 555-1234
    - Email: info@sunshinedental.com
    
    Insurance:
    - We accept most major insurance plans
    - Payment plans available for procedures over $500
    - CareCredit financing accepted
    
    Booking:
    - Call us: (305) 555-1234
    - Book online: www.sunshinedental.com/book
    - Walk-ins welcome for emergencies
    """,
    
    "conversation_style": """
    You are a friendly, professional receptionist for Sunshine Dental Clinic.
    
    Your personality:
    - Warm, empathetic, and reassuring (people are often anxious about dentists)
    - Professional but conversational
    - Patient-focused and helpful
    - Keep responses under 50 words
    
    Your responsibilities:
    1. Answer questions about services, pricing, hours, insurance
    2. If they want to book: collect name, phone, email, preferred date/time, reason for visit
    3. For emergencies: urge them to call immediately for same-day care
    4. If you don't know: "Great question! Call us at (305) 555-1234 for details"
    
    CRITICAL RULES:
    - Never give medical advice or diagnoses
    - Don't confirm appointments (say "our team will call to confirm within 2 hours")
    - Don't make up information - only use provided business details
    - Be especially empathetic for nervous patients or emergencies
    - If someone mentions pain: prioritize getting them scheduled ASAP
    """,
    
    "lead_capture_triggers": [
        "book", "appointment", "schedule", "come in", "visit",
        "emergency", "pain", "need help", "see a dentist"
    ]
}

# =============================================================================
# CONVERSATION MEMORY (In-memory - resets on restart)
# For production: Use Redis or database for persistence
# =============================================================================

conversations = {}  # Format: {session_id: [messages]}
lead_database = []  # Format: [{name, phone, email, intent, timestamp}]

# =============================================================================
# AI CHATBOT LOGIC
# =============================================================================

def get_chatbot_response(session_id, user_message):
    """
    Processes user message and returns AI response
    
    Args:
        session_id: Unique identifier for conversation
        user_message: User's message text
        
    Returns:
        AI response text
    """
    
    # Initialize conversation history if new session
    if session_id not in conversations:
        conversations[session_id] = []
    
    # Add user message to history
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Create system message with business context
    system_message = {
        "role": "system",
        "content": f"{BUSINESS_CONFIG['conversation_style']}\n\nBusiness Information:\n{BUSINESS_CONFIG['description']}"
    }
    
    # Check if lead capture should be triggered
    should_capture_lead = any(trigger in user_message.lower() 
                             for trigger in BUSINESS_CONFIG['lead_capture_triggers'])
    
    # Get AI response
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheapest, fastest model
            messages=[system_message] + conversations[session_id],
            max_tokens=150,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to history
        conversations[session_id].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # If lead capture triggered, add follow-up
        if should_capture_lead and not has_captured_lead(session_id):
            ai_response += "\n\nTo help you better, could I get your name and phone number? Our team will call you back within 2 hours to confirm your appointment."
        
        return ai_response
        
    except Exception as e:
        return f"I'm having technical difficulties right now. Please call us directly at {BUSINESS_CONFIG.get('phone', '(305) 555-1234')}. We're here to help!"

def has_captured_lead(session_id):
    """Check if we've already captured lead info for this session"""
    return any(lead.get('session_id') == session_id for lead in lead_database)

def capture_lead(session_id, lead_data):
    """Save lead information"""
    lead_data['session_id'] = session_id
    lead_data['timestamp'] = datetime.now().isoformat()
    lead_data['business'] = BUSINESS_CONFIG['name']
    lead_database.append(lead_data)
    
    # In production: Save to database, send email/SMS notification
    print(f"🔔 NEW LEAD CAPTURED: {lead_data}")
    return True

# =============================================================================
# WEB INTERFACE - Beautiful, Modern Chat UI
# =============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ business_name }} - Chat Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .chat-container {
            width: 100%;
            max-width: 450px;
            height: 700px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }
        
        .chat-header h2 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f5f5f5;
        }
        
        .message {
            margin-bottom: 20px;
            display: flex;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-bubble {
            max-width: 75%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        
        .message.user .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.bot .message-bubble {
            background: white;
            color: #333;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-bottom-left-radius: 4px;
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }
        
        .chat-input {
            display: flex;
            gap: 10px;
        }
        
        #messageInput {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            outline: none;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        
        #messageInput:focus {
            border-color: #667eea;
        }
        
        #sendButton {
            padding: 14px 28px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-size: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        #sendButton:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        #sendButton:active {
            transform: translateY(0);
        }
        
        .typing-indicator {
            display: none;
            padding: 12px 18px;
            background: white;
            border-radius: 18px;
            width: 60px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .typing-indicator span {
            height: 10px;
            width: 10px;
            background: #667eea;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            animation: typing 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
            margin-right: 0;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.7;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }
        
        .timestamp {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
            text-align: right;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 480px) {
            .chat-container {
                height: 100vh;
                border-radius: 0;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>{{ business_name }}</h2>
            <p>💬 Ask me anything! I'm here to help 24/7</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-bubble">
                    Hi! 👋 Welcome to {{ business_name }}! I'm your virtual assistant. 
                    How can I help you today?
                </div>
            </div>
        </div>
        
        <div class="chat-input-container">
            <div class="chat-input">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Type your message..."
                    autocomplete="off"
                >
                <button id="sendButton" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>
    
    <script>
        const messagesContainer = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        // Send message on Enter key
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-focus input
        messageInput.focus();
        
        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Display user message
            addMessage(message, 'user');
            messageInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send to backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();
                addMessage(data.response, 'bot');
            })
            .catch(error => {
                hideTypingIndicator();
                addMessage(
                    'Sorry, I\'m having trouble connecting. Please try again or call us directly!', 
                    'bot'
                );
                console.error('Error:', error);
            });
        }
        
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'message-bubble';
            bubbleDiv.textContent = text;
            
            messageDiv.appendChild(bubbleDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function showTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'message bot';
            indicator.id = 'typingIndicator';
            indicator.innerHTML = `
                <div class="typing-indicator" style="display: block;">
                    <span></span><span></span><span></span>
                </div>
            `;
            messagesContainer.appendChild(indicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function hideTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) {
                indicator.remove();
            }
        }
    </script>
</body>
</html>
"""

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/')
def index():
    """Render chat interface"""
    return render_template_string(
        HTML_TEMPLATE, 
        business_name=BUSINESS_CONFIG['name']
    )

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get AI response
    ai_response = get_chatbot_response(session_id, user_message)
    
    return jsonify({'response': ai_response})

@app.route('/leads', methods=['GET'])
def view_leads():
    """View captured leads (protected endpoint in production)"""
    return jsonify({
        'total_leads': len(lead_database),
        'leads': lead_database
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'business': BUSINESS_CONFIG['name'],
        'active_conversations': len(conversations),
        'total_leads': len(lead_database)
    })

# =============================================================================
# INTEGRATION EXAMPLES - Add these for premium pricing
# =============================================================================

def integrate_with_crm(lead_data):
    """
    Example: Send lead to CRM (Salesforce, HubSpot, etc.)
    Add this to capture_lead() function for $2,000-5,000 additional value
    """
    # Example HubSpot integration
    import requests
    
    hubspot_api_key = os.getenv('HUBSPOT_API_KEY')
    
    payload = {
        "properties": {
            "firstname": lead_data.get('name', '').split()[0],
            "lastname": lead_data.get('name', '').split()[-1] if len(lead_data.get('name', '').split()) > 1 else '',
            "phone": lead_data.get('phone', ''),
            "email": lead_data.get('email', ''),
            "lead_source": "Chatbot",
            "hs_lead_status": "NEW"
        }
    }
    
    # Uncomment in production:
    # response = requests.post(
    #     'https://api.hubapi.com/crm/v3/objects/contacts',
    #     headers={'Authorization': f'Bearer {hubspot_api_key}'},
    #     json=payload
    # )
    
    print(f"✅ Lead sent to CRM: {lead_data.get('name')}")

def integrate_with_calendar(appointment_data):
    """
    Example: Book appointment in Google Calendar/Calendly
    Add this for $1,500-3,000 additional value
    """
    from datetime import datetime, timedelta
    
    # Example Google Calendar integration
    # In production: Use google-api-python-client
    
    event = {
        'summary': f"Appointment - {appointment_data.get('name')}",
        'description': f"Service: {appointment_data.get('service')}\nPhone: {appointment_data.get('phone')}",
        'start': {
            'dateTime': appointment_data.get('datetime'),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': (datetime.fromisoformat(appointment_data.get('datetime')) + timedelta(hours=1)).isoformat(),
            'timeZone': 'America/New_York',
        },
        'attendees': [
            {'email': appointment_data.get('email')}
        ]
    }
    
    print(f"📅 Appointment booked: {appointment_data.get('name')} at {appointment_data.get('datetime')}")

def integrate_with_helpdesk(ticket_data):
    """
    Example: Create support ticket in Zendesk/Freshdesk
    Add this for $2,000-5,000 additional value
    """
    import requests
    
    zendesk_domain = os.getenv('ZENDESK_DOMAIN')
    zendesk_email = os.getenv('ZENDESK_EMAIL')
    zendesk_api_token = os.getenv('ZENDESK_API_TOKEN')
    
    payload = {
        "ticket": {
            "subject": f"Chatbot Support Request: {ticket_data.get('issue')}",
            "comment": {
                "body": f"Customer: {ticket_data.get('name')}\nPhone: {ticket_data.get('phone')}\n\nIssue: {ticket_data.get('description')}\n\nConversation:\n{ticket_data.get('conversation_history')}"
            },
            "priority": "normal",
            "status": "new",
            "tags": ["chatbot", "web"]
        }
    }
    
    # Uncomment in production:
    # response = requests.post(
    #     f'https://{zendesk_domain}.zendesk.com/api/v2/tickets.json',
    #     auth=(f'{zendesk_email}/token', zendesk_api_token),
    #     json=payload
    # )
    
    print(f"🎫 Support ticket created for {ticket_data.get('name')}")

def send_sms_notification(phone, message):
    """
    Example: Send SMS via Twilio
    Add this for immediate notifications
    """
    # Twilio integration (costs $0.0079 per SMS)
    from twilio.rest import Client
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Uncomment in production:
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=message,
    #     from_=twilio_phone,
    #     to=phone
    # )
    
    print(f"📱 SMS sent to {phone}: {message}")

# =============================================================================
# RAG (RETRIEVAL-AUGMENTED GENERATION) - Knowledge Base Integration
# This is what justifies $1,500-5,000 additional setup fees
# =============================================================================

def setup_rag_knowledge_base():
    """
    Setup RAG with free Supabase vector database
    Allows chatbot to answer from client's documents
    """
    # Example: Using Supabase + OpenAI embeddings
    
    # 1. Install: pip install supabase openai tiktoken
    # 2. Create Supabase project (FREE tier)
    # 3. Enable pgvector extension
    # 4. Create documents table
    
    from supabase import create_client, Client
    import tiktoken
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Example: Embed and store documents
    documents = [
        "Our dental clinic specializes in cosmetic dentistry...",
        "We offer flexible payment plans for all procedures...",
        # Add client's actual documents here
    ]
    
    for doc in documents:
        # Create embedding
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",  # $0.00002 per 1K tokens
            input=doc
        )
        embedding = embedding_response.data[0].embedding
        
        # Store in Supabase
        # Uncomment in production:
        # supabase.table('documents').insert({
        #     'content': doc,
        #     'embedding': embedding,
        #     'metadata': {'source': 'business_docs'}
        # }).execute()
    
    print("✅ RAG Knowledge Base setup complete")

def query_knowledge_base(question):
    """
    Query RAG knowledge base for relevant context
    Use this before sending to OpenAI for accurate, source-based answers
    """
    # 1. Create embedding for question
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    question_embedding = embedding_response.data[0].embedding
    
    # 2. Search Supabase for similar documents
    # Uncomment in production:
    # results = supabase.rpc('match_documents', {
    #     'query_embedding': question_embedding,
    #     'match_threshold': 0.78,
    #     'match_count': 3
    # }).execute()
    
    # 3. Return relevant context
    # context = "\n".join([doc['content'] for doc in results.data])
    # return context
    
    return "Example context from knowledge base..."

# =============================================================================
# RUN THE APPLICATION
# =============================================================================

if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════╗
║  🤖 CHATBOT EMPIRE BUILDER                            ║
║  Business: {BUSINESS_CONFIG['name']:^40} ║
╚════════════════════════════════════════════════════════╝

✅ Server Status: RUNNING
🌐 Local URL: http://localhost:5000
🛑 Stop Server: Press Ctrl+C

💰 COST BREAKDOWN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   OpenAI API: $0.002 per conversation
   Hosting (Render.com): $0/month (Free tier)
   Database (Supabase): $0/month (Free tier)
   ─────────────────────────────────────────────────────
   TOTAL MONTHLY COST: $2-10/month
   
💵 CHARGE CLIENT: $200-500/month maintenance
   YOUR PROFIT MARGIN: 95%+

🚀 DEPLOYMENT TO PRODUCTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RENDER.COM (Recommended - FREE):
   
   a. Create account at render.com
   b. Click "New +" → "Web Service"
   c. Connect your GitHub repo
   d. Settings:
      - Environment: Python
      - Build Command: pip install -r requirements.txt
      - Start Command: gunicorn app:app
   e. Add environment variables:
      - OPENAI_API_KEY=your_key
   f. Deploy! (Takes 2-3 minutes)
   
   Your chatbot will be live at: https://your-app.onrender.com

2. RAILWAY.APP (Alternative - $5/month):
   
   a. Create account at railway.app
   b. "New Project" → "Deploy from GitHub"
   c. Add environment variables
   d. Deploy automatically
   
   Your chatbot will be live at: https://your-app.up.railway.app

3. VERCEL (Frontend Only - FREE):
   
   For static sites + API routes
   Perfect for Next.js chatbots

📝 REQUIREMENTS.TXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flask==3.0.0
openai==1.12.0
python-dotenv==1.0.0
gunicorn==21.2.0
supabase==2.3.0  # If using RAG
twilio==8.11.0   # If using SMS

🎯 CUSTOMIZATION FOR EACH CLIENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Update BUSINESS_CONFIG:
   - name: Client's business name
   - industry: Their industry
   - description: Their services, hours, pricing
   - conversation_style: Their brand voice

2. Customize colors in HTML_TEMPLATE:
   - Line 35-36: Change gradient colors
   - Match client's brand colors

3. Add integrations (charge extra):
   - CRM: $2,000-5,000 setup
   - Calendar: $1,500-3,000 setup
   - Helpdesk: $2,000-5,000 setup
   - RAG Knowledge Base: $1,500-5,000 setup

4. Deploy to production:
   - 10 minutes on Render.com
   - Set up custom domain if client has one
   - Add SSL (automatic on Render)

🎨 WHITE-LABEL CUSTOMIZATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add client logo:
   - Line 95 (chat-header): Add <img> tag with logo URL
   - Match their brand colors in CSS
   - Custom domain: chatbot.clientdomain.com

💡 UPSELL OPPORTUNITIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Month 1: Basic chatbot ($1,500 setup + $200/month)
Month 3: "Let's add CRM integration" (+$3,000 + $100/month)
Month 6: "Let's add appointment booking" (+$2,000 + $50/month)
Month 9: "Let's add RAG knowledge base" (+$2,500 + $100/month)

By Month 12: Client paying $450/month (started at $200)
Your total earnings: $1,500 + $3,000 + $2,000 + $2,500 + ($450×12)
                   = $14,400 in first year from ONE client

📊 SCALING TO 50 CLIENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Setup fees (avg $2,500): $125,000
Monthly recurring (avg $350): $17,500/month = $210,000/year
TOTAL YEAR 1: $335,000

Operating costs: $5,000-15,000/year (hosting, APIs)
Net profit: $320,000-330,000 (96%+ margin)

🎓 NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Test this chatbot locally
2. Customize for a demo client (pick a niche)
3. Deploy to Render.com (FREE)
4. Create a demo video
5. Calculate ROI for your niche
6. Reach out to 100 businesses
7. Offer free demo
8. Present ROI calculation
9. Close your first 3 clients at $1,500-5,000 each
10. Scale to $300,000+/year

YOU'RE READY TO BUILD YOUR CHATBOT EMPIRE! 🚀
    """)
    
    # Run Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
