from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, origins=[
    "http://dualitymade.com",
    "https://dualitymade.com",
    "https://deluxe-concha-eb7972.netlify.app",
    "https://dualitymade.myshopify.com",
    "http://127.0.0.1:5001",
    "http://localhost:5001"
])

# Store chat history
chat_history = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shopify-support')
def shopify_support():
    return render_template('shopify_chat.html')

@app.route('/api/shopify-chat', methods=['POST'])
def handle_shopify_chat():
    data = request.json
    user_message = data.get('message', '')
    
    response = generate_shopify_response(user_message)
    
    return jsonify({'response': response})

def generate_shopify_response(message):
    message = message.lower()
    if 'shipping' in message:
        return "We offer free shipping on orders over $100. Standard shipping takes 3-5 business days."
    elif 'return' in message or 'refund' in message:
        return "Our return policy allows returns within 30 days of purchase. Items must be unused with original tags. Please email support@dualitymade.com to initiate a return."
    elif 'order' in message or 'tracking' in message:
        return "To check your order status, please email support@dualitymade.com with your order number."
    elif 'contact' in message:
        return "You can reach us at support@dualitymade.com for any questions or concerns."
    elif 'product' in message or 'items' in message:
        return "We offer a variety of high-quality clothing items. You can view our full collection on our website. For specific product questions, please email support@dualitymade.com"
    else:
        return "How can I help you with your shopping today? I can assist with shipping, returns, orders, and product information. For specific questions, please email support@dualitymade.com"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        # Get or initialize chat history for this session
        if session_id not in chat_history:
            chat_history[session_id] = []
        
        # Generate response based on user message
        response = get_enhanced_response(user_message, session_id)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def get_enhanced_response(message: str, session_id: str) -> str:
    """Enhanced response logic with context awareness"""
    message = message.lower()
    chat_history[session_id].append(message)
    
    # Product-specific responses
    if 'product a' in message or 'premium' in message:
        return ("Product A is our premium solution that includes:\n"
                "• Advanced features\n"
                "• 24/7 priority support\n"
                "• Custom integrations\n"
                "Would you like to know about pricing or see a demo?")
    
    elif 'product b' in message or 'standard' in message:
        return ("Product B is our standard package offering:\n"
                "• Core features\n"
                "• Business hours support\n"
                "• Basic integrations\n"
                "Would you like to know more about the features?")
    
    elif 'product c' in message or 'basic' in message:
        return ("Product C is our basic option, perfect for startups:\n"
                "• Essential features\n"
                "• Email support\n"
                "• Self-service setup\n"
                "Would you like to see the pricing?")
    
    elif any(word in message for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your customer service assistant. How can I help you today?"
    
    elif any(word in message for word in ['product', 'service']):
        return ("We offer several products and services:\n\n"
                "1. Product A - Premium solution\n"
                "2. Product B - Standard package\n"
                "3. Product C - Basic option\n\n"
                "Which would you like to know more about?")
    
    elif any(word in message for word in ['price', 'cost', 'pricing']):
        return ("Our pricing options:\n\n"
                "• Basic Plan: $29/month\n"
                "• Pro Plan: $59/month\n"
                "• Enterprise: Custom pricing\n\n"
                "Would you like more details about any specific plan?")
    
    elif any(word in message for word in ['contact', 'reach', 'email', 'phone']):
        return ("You can reach us through:\n\n"
                "• Email: support@dualitymade.com\n"
                "• Live Chat: Available 24/7\n\n"
                "How would you prefer to connect with us?")
    
    elif any(word in message for word in ['help', 'support', 'issue']):
        return ("I'll be happy to help! Please let me know what type of assistance you need:\n\n"
                "1. Technical Support\n"
                "2. Account Help\n"
                "3. Billing Questions\n"
                "4. General Information")
    
    else:
        return ("I'm here to help with:\n\n"
                "• Product Information\n"
                "• Pricing Details\n"
                "• Technical Support\n"
                "• General Inquiries\n\n"
                "What would you like to know more about?")

# Create the templates directory and index.html
os.makedirs('templates', exist_ok=True)

# Create index.html
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Customer Service Bot</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .chat-message {
            margin: 10px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
        }
        .bot-message {
            background-color: #f5f5f5;
            margin-right: auto;
        }
        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .typing-indicator {
            padding: 10px;
            display: none;
        }
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: #90cdf4;
            border-radius: 50%;
            margin-right: 5px;
            animation: typing 1s infinite;
        }
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto p-4 max-w-4xl">
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h1 class="text-2xl font-bold mb-4 text-center text-blue-600">AI Customer Service Assistant</h1>
            
            <!-- Chat Window -->
            <div class="chat-container mb-4" id="chatContainer">
                <div id="messages"></div>
                <div class="typing-indicator" id="typingIndicator">
                    <span></span>
                    <span style="animation-delay: 0.2s"></span>
                    <span style="animation-delay: 0.4s"></span>
                </div>
            </div>
            
            <!-- Input Area -->
            <div class="flex gap-2">
                <input type="text" 
                       id="userInput" 
                       class="flex-1 p-3 border rounded-lg focus:outline-none focus:border-blue-500"
                       placeholder="Type your message here...">
                <button onclick="sendMessage()" 
                        class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    Send
                </button>
            </div>
            
            <!-- Quick Actions -->
            <div class="mt-4">
                <h3 class="text-sm font-semibold text-gray-600 mb-2">Quick Actions:</h3>
                <div class="flex flex-wrap gap-2">
                    <button onclick="sendQuickMessage('Tell me about your products')" 
                            class="bg-gray-100 px-3 py-1 rounded-full text-sm hover:bg-gray-200 transition-colors">
                        Products
                    </button>
                    <button onclick="sendQuickMessage('What are your prices?')" 
                            class="bg-gray-100 px-3 py-1 rounded-full text-sm hover:bg-gray-200 transition-colors">
                        Pricing
                    </button>
                    <button onclick="sendQuickMessage('I need support')" 
                            class="bg-gray-100 px-3 py-1 rounded-full text-sm hover:bg-gray-200 transition-colors">
                        Support
                    </button>
                    <button onclick="sendQuickMessage('How can I contact you?')" 
                            class="bg-gray-100 px-3 py-1 rounded-full text-sm hover:bg-gray-200 transition-colors">
                        Contact
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const chatContainer = document.getElementById('chatContainer');
        const typingIndicator = document.getElementById('typingIndicator');
        
        // Generate a unique session ID
        const sessionId = 'session_' + Math.random().toString(36).substring(2);

        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        function addMessage(text, isUser = false) {
            const div = document.createElement('div');
            div.className = `chat-message ${isUser ? 'user-message' : 'bot-message'}`;
            div.innerText = text;
            messages.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // Clear input
            userInput.value = '';

            // Add user message
            addMessage(message, true);

            // Show typing indicator
            showTypingIndicator();

            try {
                // Send to server
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: message,
                        session_id: sessionId
                    })
                });

                const data = await response.json();
                
                // Hide typing indicator
                hideTypingIndicator();

                // Add bot response
                if (data.status === 'success') {
                    addMessage(data.response);
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.');
                }

            } catch (error) {
                hideTypingIndicator();
                addMessage('Sorry, there was an error processing your message.');
                console.error('Error:', error);
            }
        }

        function sendQuickMessage(message) {
            userInput.value = message;
            sendMessage();
        }

        // Handle Enter key
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Initial greeting
        addMessage("Hello! I'm your AI customer service assistant. How can I help you today?");
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("\nStarting Customer Service Bot...")
    print("\nAccess the bot at: http://127.0.0.1:5001")
    app.run(debug=True, port=5001)