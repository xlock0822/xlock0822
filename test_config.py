from dotenv import load_dotenv
import os
import sys

def test_configuration():
    print("\n=== Testing Configuration ===\n")
    
    # 1. Test .env loading
    print("1. Testing .env file loading...")
    try:
        load_dotenv()
        print("✅ .env file loaded successfully")
    except Exception as e:
        print(f"❌ Error loading .env file: {str(e)}")
        return

    # 2. Check required variables
    required_vars = {
        'DISCORD_TOKEN': '****',  # We'll show first 4 chars only
        'FLASK_SECRET_KEY': '****',
        'OPENAI_API_KEY': '****',
        'FLASK_DEBUG': 'full',  # We'll show full value
        'PORT': 'full'
    }

    print("\n2. Checking environment variables...")
    all_vars_present = True
    for var, display_type in required_vars.items():
        value = os.getenv(var)
        if value:
            if display_type == 'full':
                print(f"✅ {var}: {value}")
            else:
                print(f"✅ {var}: {value[:4]}...")
        else:
            print(f"❌ {var} is not set")
            all_vars_present = False

    # 3. Test variable types and formats
    print("\n3. Validating variable formats...")
    if os.getenv('PORT'):
        try:
            port = int(os.getenv('PORT'))
            print(f"✅ PORT is valid integer: {port}")
        except ValueError:
            print("❌ PORT must be a number")
            all_vars_present = False

    if os.getenv('FLASK_DEBUG'):
        debug = os.getenv('FLASK_DEBUG').lower() in ['true', '1', 'yes']
        print(f"✅ FLASK_DEBUG is valid boolean: {debug}")

    # 4. Check token lengths
    print("\n4. Checking token lengths...")
    if os.getenv('DISCORD_TOKEN'):
        token_length = len(os.getenv('DISCORD_TOKEN'))
        print(f"✅ Discord token length: {token_length} characters")
        if token_length < 50:
            print("⚠️ Warning: Discord token seems shorter than expected")

    if os.getenv('FLASK_SECRET_KEY'):
        secret_length = len(os.getenv('FLASK_SECRET_KEY'))
        print(f"✅ Flask secret key length: {secret_length} characters")
        if secret_length < 32:
            print("⚠️ Warning: Flask secret key should be at least 32 characters")

    # 5. Summary
    print("\n=== Configuration Test Summary ===")
    if all_vars_present:
        print("✅ All required variables are set")
        print("✅ Configuration test passed")
    else:
        print("❌ Some required variables are missing")
        print("❌ Configuration test failed")

    # 6. Directory structure check
    print("\n5. Checking directory structure...")
    required_dirs = ['src', 'templates', 'static', 'logs', 'data']
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory is missing")
            try:
                os.makedirs(directory)
                print(f"  └─ Created {directory}/ directory")
            except Exception as e:
                print(f"  └─ Error creating directory: {str(e)}")

if __name__ == "__main__":
    try:
        test_configuration()
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        sys.exit(1)