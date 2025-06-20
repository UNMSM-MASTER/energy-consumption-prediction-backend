import firebase_admin
from firebase_admin import credentials, firestore
from app.config.secrets import config

if not firebase_admin._apps:
    cred = credentials.Certificate(config.get("FIREBASE_CREDENTIALS"))
    firebase_admin.initialize_app(cred)

app = firebase_admin.get_app()
db = firestore.client()