from firebase_admin import db

from .firebase_config import get_firestore_client
from .logger import logger
# # Inicialize o SDK do Firebase Admin com suas credenciais
# cred = credentials.Certificate('Fluxo_caixa/assets/flet-login-16b06-firebase-adminsdk-i12wz-c4d92e5b8c.json')
# firebase_admin.initialize_app(cred, {'databaseURL': 'https://flet-login-16b06-default-rtdb.firebaseio.com/'})

db = get_firestore_client()

class Service:
    def __init__(self, nome:str, preco:float, duracao:int, scheduling:bool):
        self.nome = nome
        self.preco = preco
        self.duracao = duracao
        self.scheduling = scheduling
        self.user_data = {}
        self.uid = ""
        self.tipo_usuario = 'cliente'

    def criar_servico(self):
        doc_ref = db.collection('servico').document()

        doc_ref.set({
            'nome': self.nome,
            'preco': self.preco,
            'duracao': self.duracao,
            'permitir_agendamento': self.scheduling,
                
        })
        logger.log('create', 'servico', doc_ref.id, {
            'nome': self.nome,
            'preco': self.preco,
            'duracao': self.duracao,
            'permitir_agendamento': self.scheduling,
        })
        return doc_ref.get().to_dict()

class UpdateService:
    def __init__(self, nome:str, preco:float, duracao:int, scheduling:bool, id_service):
        self.nome = nome
        self.preco = preco
        self.duracao = duracao
        self.scheduling = scheduling
        self.id_service = id_service
        self.user_data = {}
        self.uid = ""
        self.tipo_usuario = 'cliente'

    def atualizar_servico(self):
        doc_ref = db.collection('servico').document(self.id_service)

        doc_ref.update({
            'nome': self.nome,
            'preco': self.preco,
            'duracao': self.duracao,
            'permitir_agendamento': self.scheduling,
                
        })
        logger.log('update', 'servico', self.id_service, {
            'nome': self.nome,
            'preco': self.preco,
            'duracao': self.duracao,
            'permitir_agendamento': self.scheduling,
        })
        return doc_ref.get().to_dict()
    
# Exemplo de uso da função
# novo_servico = Service("Corte de cabelo3", 40.90, 30)
# novo_servico.criar_servico()

# novo_usuario = User('teste5@teste.com', '12345678', "11-48214286", "Mateus")
# novo_usuario.criar_usuario()
# if novo_usuario.uid:
#     print('Usuário criado com sucesso:', novo_usuario.uid)