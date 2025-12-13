import firebase_admin
from firebase_admin import credentials
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

cred = credentials.Certificate(BASE_DIR / "firebase-service-account.json")
firebase_admin.initialize_app(cred)
