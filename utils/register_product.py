from firebase_admin import db

from .firebase_config import get_firestore_client
from .logger import logger

# # Inicialize o SDK do Firebase Admin com suas credenciais
# cred = credentials.Certificate('Fluxo_caixa/assets/flet-login-16b06-firebase-adminsdk-i12wz-c4d92e5b8c.json')
# firebase_admin.initialize_app(cred, {'databaseURL': 'https://flet-login-16b06-default-rtdb.firebaseio.com/'})

db = get_firestore_client()

class Product:
    def __init__(self, nome:str, preco:float, checkbox:bool):
        self.nome = nome
        self.preco = preco
        self.checkbox_venda = checkbox
        self.user_data = {}
        self.uid = ""

    def criar_produto(self):
        doc_ref = db.collection('produto').document()
        verifica_existe = doc_ref.get().to_dict()
        if verifica_existe:
            return None
        doc_ref.set({
            'nome': self.nome,
            'preco': self.preco,
            'permitir_venda': self.checkbox_venda,           
        })
        logger.log('create', 'produto', doc_ref.id, {
            'nome': self.nome,
            'preco': self.preco,
            'permitir_venda': self.checkbox_venda,
        })
        return doc_ref.get().to_dict()

class UpdateProduct:
    def __init__(self, nome:str, preco:float, checkbox:bool, id_produto):
        self.nome = nome
        self.preco = preco
        self.checkbox_venda = checkbox
        self.id_produto = id_produto
        self.user_data = {}
        self.uid = ""

    def atualizar_produto(self):

        # Salva as informações do usuário no Firestore, exceto a senha
        doc_ref = db.collection('produto').document(self.id_produto)

        doc_ref.update({
            'nome': self.nome,
            'preco': self.preco,
            'permitir_venda': self.checkbox_venda,           
        })
        logger.log('update', 'produto', self.id_produto, {
            'nome': self.nome,
            'preco': self.preco,
            'permitir_venda': self.checkbox_venda,
        })
        return doc_ref.get().to_dict()
# Exemplo de uso da função
# novo_servico = Service("Corte de cabelo3", 40.90, 30)
# novo_servico.criar_servico()

# novo_usuario = User('teste5@teste.com', '12345678', "11-48214286", "Mateus")
# novo_usuario.criar_usuario()
# if novo_usuario.uid:
#     print('Usuário criado com sucesso:', novo_usuario.uid)