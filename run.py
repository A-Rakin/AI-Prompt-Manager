import os
from app import create_app

# ==============================================================================
# PromptForge - Application Launcher Script
# ==============================================================================
# This script serves as the main entry point to start the Flask development server.
#
# Usage:
#   python run.py
# ==============================================================================

# Determine runtime environment ('development', 'production', or 'testing')
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Launch local development web server on port 5000 with live reloading enabled
    print(f"Starting PromptForge application server in [{env}] mode...")
    app.run(host='127.0.0.1', port=5000, debug=True)
