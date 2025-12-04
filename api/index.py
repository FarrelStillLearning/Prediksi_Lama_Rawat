# Vercel serverless function entry point
from backend.app_flask import app

# Vercel expects a variable named 'app' or a handler function
# Flask app is already named 'app', so this will work directly
