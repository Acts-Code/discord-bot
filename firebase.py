import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

firebase_json = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)

db = firestore.client()
