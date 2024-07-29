# firebase_config.py
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

cred = credentials.Certificate({
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "aunt_provider_x509_cert_url": os.getenv("FIREBASE_AUNT_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
})


# Inicialize o SDK do Firebase Admin com suas credenciais
# cred = credentials.Certificate('assets/flet-login-16b06-firebase-adminsdk-i12wz-c4d92e5b8c.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://flet-login-16b06-default-rtdb.firebaseio.com/'})


def initialize_firebase():
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        db = firestore.client()

# Retorna a instância do cliente do Firestore
def get_firestore_client():
    initialize_firebase()
    return firestore.client()