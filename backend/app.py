from flask import Flask
import os

from flask_cors import CORS
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as requests

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "https://playlist-transfer-lovat.vercel.app"}}, supports_credentials=True)
app.secret_key = os.getenv("CLIENT_SECRET")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP traffic for local dev

# app.config["SESSION_COOKIE_DOMAIN"] = ".vercel.app"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True


# Import your routes
import auth
import scraping
import youtube
import logging_manager

# Register routes with the app
app.register_blueprint(auth.auth_bp)
app.register_blueprint(scraping.scraping_bp)
app.register_blueprint(youtube.youtube_bp)
app.register_blueprint(logging_manager.logging_bp)
