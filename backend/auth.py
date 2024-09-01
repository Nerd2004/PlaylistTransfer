from flask import Blueprint, jsonify, redirect, session, request, abort
from pathlib import Path
import os
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from functools import wraps

auth_bp = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = os.getenv('CLIENT_ID')

client_secrets_file = Path(__file__).parent / "client_secret.json"
client_secrets = {
    "web": {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "project_id": os.getenv("PROJECT_ID"),
    }
}

# Initialize Flow directly with client secrets
flow = Flow.from_client_config(
    client_config=client_secrets,
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/youtube"],
    redirect_uri=client_secrets["web"]["redirect_uri"]
)

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        return function(*args, **kwargs)
    return decorated_function

@auth_bp.route("/login")
def login():
    # authorization_url, state = flow.authorization_url()
    authorization_url, state = flow.authorization_url(
      access_type='offline',
      include_granted_scopes='true',
      approval_prompt='force')
    session["state"] = state
    return redirect(authorization_url)

@auth_bp.route('/check')
@login_required
def user_info():
    data = {
        "name": session.get("name"),
        "email": session.get("email"),
        "picture": session.get("picture"),
    }
    return jsonify(data), 200


@auth_bp.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials

    session['refresh_token']=credentials.refresh_token
    session['token'] = credentials.token
    session['token_expiry'] = int(credentials.expiry.timestamp())
 
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=google_requests.Request(),
        audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["picture"] = id_info.get("picture")
    session["email"] = id_info.get("email")
    return redirect("/")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@auth_bp.route("/")
def index():
    return redirect("https://playlist-transfer-lovat.vercel.app")