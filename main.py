# --- START OF FILE main.py ---

from dotenv import load_dotenv

# This line reads the .env file and sets the environment variables
load_dotenv()

from app import create_app

# Create the application instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Now you can just run this file directly!
    app.run(host='0.0.0.0', port=5000, debug=True)
