import os
import requests
import json
from dotenv import load_dotenv
from firebase_admin import auth
from datetime import datetime, timedelta

from .firebase_config import get_firestore_client

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class User:
    def __init__(self, email:str, senha:str):
        # Inicializa a classe com e-mail e senha do usuário
        self.email = email
        self.senha = senha
        self.idToken = ""  # Token de ID usado para autenticação no Firebase
        self.user_data = {}  # Dados do usuário obtidos do Firebase
        self.localId = ""  # ID local do usuário no Firebase
        self.FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")  # Chave da API Web do Firebase

    def verifica_email_existente(self):
            try:
                # Tenta obter o usuário pelo e-mail
                user = auth.get_user_by_email(self.email)
                return True  # O e-mail existe no banco de dados
            except auth.UserNotFoundError:
                return False  # O e-mail não existe no banco de dados

    def enviar_email_verificacao(self):
        # Define os cabeçalhos para a requisição HTTP
        headers = {
            'Content-Type': 'application/json',
        }
        # Define os dados para a requisição HTTP
        data = {
            'requestType': 'VERIFY_EMAIL',  # Tipo de requisição para verificação de e-mail
            'idToken': self.idToken,  # Token de ID necessário para a verificação de e-mail
        }
        # Faz uma requisição POST para enviar o e-mail de verificação
        response = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode', params={"key": self.FIREBASE_WEB_API_KEY}, headers=headers, json=data)
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            return True  # Retorna verdadeiro se o e-mail de verificação foi enviado com sucesso
        else:
            return False  # Retorna falso se houve falha ao enviar o e-mail de verificação
        
    def check_email_verification(self):
        try:
            # Obtém o usuário pelo e-mail usando o SDK firebase_admin
            user = auth.get_user_by_email(self.email)
            # Verifica se o e-mail foi verificado
            if user.email_verified:
                return True  # Retorna verdadeiro se o e-mail foi verificado
            else:
                return False  # Retorna falso se o e-mail não foi verificado
        except auth.AuthError as e:
            return False
        
    def login_firebase(self):
        if self.verifica_email_existente() is False:
            return "email_not_found"
        
        # Define os dados da requisição para login no Firebase
        payload = json.dumps({
            "email": self.email,
            "password": self.senha,
            "returnSecureToken": True  # Indica que um token seguro deve ser retornado na resposta
        })
        
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"  # URL da API REST para login com senha no Firebase
        
        r = requests.post(rest_api_url, params={"key": self.FIREBASE_WEB_API_KEY}, data=payload)  # Faz uma requisição POST para login
        
        if r.status_code != 200:
            return "incorrect_password"
        
        self.idToken = r.json()['idToken']  # Atualiza o token de ID com a resposta do Firebase
        self.localId = r.json()['localId']  # Atualiza o ID local com a resposta do Firebase
        self.user_data = r.json()  # Atualiza os dados do usuário com a resposta do Firebase
        
        
        if not self.check_email_verification():
            self.enviar_email_verificacao()  # Envia um e-mail de verificação se o e-mail não estiver verificado
            return "email_not_verified"
            
        else:
            db = get_firestore_client()  # Obtém uma instância do cliente Firestore
                
            if 'funcaoID' not in self.user_data:
                doc_ref = db.collection('usuarios').document(self.user_data['localId'])  # Referência ao documento do usuário no Firestore
                    
                doc = doc_ref.get()  # Obtém o documento
                    
                if doc.exists:
                    user_doc = doc.to_dict()
                # Se o documento existir, adiciona a key 'funcaoID' na variável user
                    expiration_time = datetime.now() + timedelta(hours=1)
                    self.user_data['funcaoID'] = user_doc.get('funcaoID')
                    self.user_data['expiration_time'] = expiration_time.strftime("%Y-%m-%d %H:%M:%S")
                    self.user_data['name'] = user_doc.get('nome')
                    self.user_data['phone_number'] = user_doc.get('telefone')
                else:
                    ...
            return self.user_data
    
    def refresh_token(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refreshToken,
        }
        response = requests.post(
            f'https://securetoken.googleapis.com/v1/token?key={self.FIREBASE_WEB_API_KEY}',
            headers=headers, data=json.dumps(data)
        )
        if response.status_code == 200:
            new_tokens = response.json()
            self.idToken = new_tokens['id_token']
            self.refreshToken = new_tokens['refresh_token']
            return self.idToken
        else:
            return None
        
    def validate_token(self):
        try:
            auth.verify_id_token(self.idToken)
            return True
        except auth.InvalidIdTokenError:
            if self.refreshToken:  # Verifica se o refreshToken não está vazio
                new_token = self.refresh_token()
                if new_token:
                    self.idToken = new_token
                    return True
            return False

class ForgetPassword:
    def __init__(self, email:str):
        # Inicializa a classe com e-mail e senha do usuário
        self.email = email
        self.FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")  # Chave da API Web do Firebase

    def verifica_email_existente(self):
            try:
                # Tenta obter o usuário pelo e-mail
                user = auth.get_user_by_email(self.email)
                return True  # O e-mail existe no banco de dados
            except auth.UserNotFoundError:
                return False  # O e-mail não existe no banco de dados

    def redefine_password(self):
        if self.verifica_email_existente():
            url = 'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode'
            headers = {'Content-Type': 'application/json'}
            data = {
                'requestType': 'PASSWORD_RESET',
                'email': self.email
            }
            response = requests.post(url, params={'key': self.FIREBASE_WEB_API_KEY}, headers=headers, json=data)
                
            return response.status_code == 200  # Retorna verdadeiro se o e-mail foi enviado com sucesso
        else:
            return False  # Retorna falso se o e-mail não existir no banco de dados
# # Exemplo de uso:
# usuario = User('teste@teste.com', '12345678')
# usuario.login_firebase()
# print(usuario.idToken)
# print()
# print(usuario.localId)
# print()
# print(usuario.user_data)