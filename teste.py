# main.py
import flet as ft
from utils.firebase_config import initialize_firebase
import requests
from firebase_admin import auth

# Inicializar o Firestore
initialize_firebase()

def main(page: ft.Page):
    def on_google_login(e):
        # URL para a página de login do Google
        google_login_url = "https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=email&response_type=code"
        
        # Abrir a URL de login do Google no navegador
        page.launch_url(google_login_url)

    def on_login_success(code):
        # Trocar o código de autorização por um token de ID
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': code,
            'client_id': "YOUR_CLIENT_ID",
            'client_secret': "YOUR_CLIENT_SECRET",
            'redirect_uri': "YOUR_REDIRECT_URI",
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()
        
        # Verificar o token no Firebase
        id_token = tokens['id_token']
        decoded_token = auth.verify_id_token(id_token)
        user_uid = decoded_token['uid']
        
        # Mostrar o UID do usuário na tela
        page.controls.append(ft.Text(f'Login bem-sucedido! UID do usuário: {user_uid}'))
        page.update()

    # Botão para login com Google
    google_login_button = ft.ElevatedButton(text="Login com Google", on_click=on_google_login)

    page.add(google_login_button)

    # Verificar se o código de autorização está na URL de retorno
    if "code" in page.query_params:
        auth_code = page.query_params["code"]
        on_login_success(auth_code)

ft.app(target=main)
