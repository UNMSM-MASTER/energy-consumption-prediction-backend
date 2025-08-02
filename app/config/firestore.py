import firebase_admin
from firebase_admin import credentials, firestore
import os
from app.config.settings import get_settings

if not firebase_admin._apps:
    # Use the JSON file for credentials
    cred_path = "firebase-credentials.json"
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        # Fallback to environment variables if file doesn't exist
        settings = get_settings()
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    
    firebase_admin.initialize_app(cred)

app = firebase_admin.get_app()
db = firestore.client()