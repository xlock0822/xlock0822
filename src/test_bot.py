from modules.context_analyzer import ContextAnalyzer
from modules.response_formatter import ResponseFormatter

def test_basic_functionality():
    # Initialize components
    analyzer = ContextAnalyzer()
    formatter = ResponseFormatter()

    # Test messages
    test_messages = [
        "What are your product prices?",
        "I need help with my account",
        "There's an error in my bill",
        "Thank you for your help!"
    ]

    print("\nTesting basic bot functionality:")
    print("--------------------------------")

    for message in test_messages:
        print(f"\nTesting message: '{message}'")
        
        # Analyze message
        analysis = analyzer.analyze(message)
        
        # Create test response data
        response_data = {
            'main_response': f"Responding to: {message}",
            'details': {
                'Intent': analysis['intent'],
                'Urgency': 'Urgent' if analysis['urgency'] else 'Normal',
                'Sentiment': analysis['sentiment']
            },
            'suggestions': ['Would you like to know more?', 'Can I help with anything else?']
        }

        # Format response
        embed = formatter.format_response(response_data, analysis['intent'])
        
        print(f"Intent detected: {analysis['intent']}")
        print(f"Urgency: {analysis['urgency']}")
        print(f"Sentiment: {analysis['sentiment']}")
        print("Embed created successfully")

if __name__ == "__main__":
    test_basic_functionality()
    