from firebase_admin import db

from .logger import logger
from .firebase_config import get_firestore_client

db = get_firestore_client()

class CreateExpense:
    def __init__(self, data_despesa,
                 mes_despesa,
                 ano_despesa,
                 id_categoria,
                 categoria,
                 preco,
                 descricao):
        self.data_despesa = data_despesa
        self.mes_despesa = mes_despesa
        self.ano_despesa = ano_despesa
        self.id_categoria = id_categoria
        self.categoria = categoria
        self.preco = preco
        self.descricao = descricao

    def registrar_despesa(self):
        despesa = {
            'categoria_id': self.id_categoria,
            'categoria_nome': self.categoria,
            'descricao': self.descricao,
            'valor': self.preco,
            'data': self.data_despesa
        }
        expense_ref = db.collection('despesas').document(self.ano_despesa).collection(self.mes_despesa).add(despesa)
        logger.log('create', 'despesas', expense_ref[1].id, despesa)
        return True

class UpdateExpense:
    def __init__(self, id_despesa,
                 mes_despesa,
                 ano_despesa,
                 id_categoria,
                 categoria,
                 preco,
                 descricao):
        self.id_despesa = id_despesa
        self.mes_despesa = mes_despesa
        self.ano_despesa = ano_despesa
        self.id_categoria = id_categoria
        self.categoria = categoria
        self.preco = preco
        self.descricao = descricao

    def atualizar_despesa(self):
        expense_ref = db.collection('despesas').document(self.ano_despesa).collection(self.mes_despesa).document(self.id_despesa)        

        expense_ref.update({
            'categoria_id': self.id_categoria,
            'categoria_nome': self.categoria,
            'descricao': self.descricao,
            'valor': self.preco,
        }) 
        logger.log('update', 'despesas', self.id_despesa, {
            'categoria_id': self.id_categoria,
            'categoria_nome': self.categoria,
            'descricao': self.descricao,
            'valor': self.preco,
        })
        return True
    
class CreateCategory:
    def __init__(self, nome:str, checkbox:bool):
        self.nome = nome
        self.checkbox = checkbox

        self.user_data = {}
        self.uid = ""

    def criar_categoria(self):
        categoria = {'nome': self.nome,
                     'ativo': self.checkbox}
        doc_ref = db.collection('categorias').add(categoria)
        logger.log('create', 'categorias', doc_ref[1].id, categoria)
        return True
    
class UpdateCategory:
    def __init__(self, nome:str, checkbox:bool, id_categoria):
        self.nome = nome
        self.checkbox = checkbox
        self.id_categoria = id_categoria

        self.user_data = {}
        self.uid = ""

    def atualizar_categoria(self):
        categoria_ref = db.collection('categorias').document(self.id_categoria)
        categoria_ref.update({
            'nome': self.nome,
            'ativo': self.checkbox})
        logger.log('update', 'categorias', self.id_categoria, {'nome': self.nome, 'ativo': self.checkbox})
        return True