from .firebase_config import get_firestore_client
from .logger import logger
# # Inicialize o SDK do Firebase Admin com suas credenciais
# cred = credentials.Certificate('Fluxo_caixa/assets/flet-login-16b06-firebase-adminsdk-i12wz-c4d92e5b8c.json')
# firebase_admin.initialize_app(cred, {'databaseURL': 'https://flet-login-16b06-default-rtdb.firebaseio.com/'})

db = get_firestore_client()

class Scheduling:
    def __init__(self, user_data, name, phone, service_choose_id, day_choose, hour_choose, collaborator_choose, service_dict):
        self.user_data = user_data
        self.name = name
        self.phone = phone
        self.service_choose_id = service_choose_id
        self.day_choose = day_choose
        self.hour_choose = hour_choose
        self.collaborator_choose = collaborator_choose
        self.service_dict = service_dict
        self.status_scheduling = "Em andamento"
        self.user_id = self.user_data['localId']
        self.service_name = self.service_dict['nome']
        self.service_price = self.service_dict['preco']
        self.service_time = self.service_dict['duracao']
        self.uid = ""
        self.scheduling_data = {}

    def create_scheduling(self):
        scheduling_ref = db.collection('agendamentos').document()    
        scheduling_ref.set({
            'user_id': self.user_id,
            'nome': self.name,
            'telefone': self.phone,
            'servico_id': self.service_choose_id,
            'nome_servico': self.service_name,
            'duracao_servico': self.service_time,
            'preco_servico': self.service_price,
            'data': self.day_choose,
            'horario': self.hour_choose,
            'colaborador_id': self.collaborator_choose,
            'status_agendamento': self.status_scheduling
        })
        self.scheduling_data = scheduling_ref.get().to_dict()
        logger.log('create', 'agendamentos', scheduling_ref.id, self.scheduling_data)
        return self.scheduling_data

class UpdateScheduling:
    def __init__(self, agendamento_id, user_data, name, phone, service_choose_id, day_choose, hour_choose, collaborator_choose, service_dict):
        self.agendamento_id = agendamento_id
        self.user_data = user_data
        self.name = name
        self.phone = phone
        self.service_choose_id = service_choose_id
        self.day_choose = day_choose
        self.hour_choose = hour_choose
        self.collaborator_choose = collaborator_choose
        self.service_dict = service_dict
        self.status_scheduling = "Em andamento"
        self.user_id = self.user_data['localId']
        self.service_name = self.service_dict['nome']
        self.service_price = self.service_dict['preco']
        self.service_time = self.service_dict['duracao']
        self.uid = ""
        self.scheduling_data = {}

    def update_scheduling(self):
        scheduling_ref = db.collection('agendamentos').document(self.agendamento_id)    
        scheduling_ref.update({
            'user_id': self.user_id,
            'nome': self.name,
            'telefone': self.phone,
            'servico_id': self.service_choose_id,
            'nome_servico': self.service_name,
            'duracao_servico': self.service_time,
            'preco_servico': self.service_price,
            'data': self.day_choose,
            'horario': self.hour_choose,
            'colaborador_id': self.collaborator_choose,
            'status_agendamento': self.status_scheduling
        })
        self.scheduling_data = scheduling_ref.get().to_dict()
        logger.log('update', 'agendamentos', self.agendamento_id, self.scheduling_data)
        return self.scheduling_data

class FinishScheduling:
    def __init__(self, agendamento_id, collaborator_id, name_service, servico_id, services_select, products_select, price_services:float, price_products:float, discount:float, price_total:float):
        self.agendamento_id = agendamento_id
        self.colaborador_id = collaborator_id
        self.name_service = name_service
        self.servico_id = servico_id
        self.services_select = services_select
        self.products_select = products_select
        self.price_services = price_services
        self.price_products = price_products
        self.discount = discount
        self.price_total = price_total
        self.uid = ""
        self.scheduling_data = {}

    def finish_scheduling(self):
        scheduling_ref = db.collection('agendamentos').document(self.agendamento_id)
        scheduling = scheduling_ref.get().to_dict()
        dia, mes, ano = scheduling.get('data').split('-')
        if scheduling and scheduling['status_agendamento'] != 'Concluido':
            scheduling_ref.update(
                {'status_agendamento': 'Concluido',
                 'colaborador_id': self.colaborador_id,
                 'nome_servico': self.name_service,
                 'servico_id': self.servico_id,
                 'servicos': self.services_select,
                 'preco_servico': self.price_services,
                 'produtos' : self.products_select,
                 'desconto': self.discount,
                 'total': self.price_total}
            )
        
            transacao = {
                'agendamento_id': self.agendamento_id,
                'colaborador_id': self.colaborador_id,
                'data': scheduling['data'],
                'preco_servico': self.price_services,
                'preco_produtos': self.price_products,
                'desconto': self.discount,
                'total': self.price_total
            }
            db.collection('transacoes').document(ano).collection(mes).add(transacao)
            logger.log('finish', 'agendamentos', self.agendamento_id, scheduling_ref.get().to_dict())
            logger.log('create', 'transacoes', transacao['agendamento_id'], transacao)
        
        return True

class CreateService:
    def __init__(self, collaborator_id, data, services_select, products_select, price_service:float, price_products:float, discount:float, price_total:float):
        self.collaborator_id = collaborator_id
        self.data = data
        self.products_select = products_select
        self.services_select = services_select
        self.price_service = price_service
        self.price_products = price_products
        self.discount = discount
        self.price_total = price_total
        self.nome_cliente = "Cliente não informado"
        self.horario = "Horário não informado"
        self.uid = ""
        self.scheduling_data = {}

    def finish_service(self):
        dia, mes, ano = self.data.split('-')
        agendamento = {
            'colaborador_id': self.collaborator_id,
            'data': self.data,
            'servicos': self.services_select,
            'preco_servico': self.price_service,
            'produtos': self.products_select,
            'preco_produtos': self.price_products,
            'desconto': self.discount,
            'total': self.price_total,
            'status_agendamento': 'Concluido'
        }
        scheduling_ref = db.collection('agendamentos').add(agendamento)
        
        transacao = {
            'agendamento_id': scheduling_ref[1].id,
            'colaborador_id': self.collaborator_id,
            'data': self.data,
            'preco_servico': self.price_service,
            'preco_produtos': self.price_products,
            'desconto': self.discount,
            'total': self.price_total
        }
        
        db.collection('transacoes').document(ano).collection(mes).add(transacao)
        logger.log('create', 'agendamentos', scheduling_ref[1].id, agendamento)
        logger.log('create', 'transacoes', transacao['agendamento_id'], transacao)

        return True

class CancelScheduling:
    def __init__(self, agendamento_id):
        self.agendamento_id = agendamento_id
        self.uid = ""
        self.scheduling_data = {}

    def cancel_scheduling(self):
        scheduling_ref = db.collection('agendamentos').document(self.agendamento_id)
        scheduling = scheduling_ref.get().to_dict()
        dia, mes, ano = scheduling.get('data').split('-')
        if scheduling and scheduling['status_agendamento'] != 'Concluido':
            scheduling_ref.update({'status_agendamento': 'Cancelado'})
            logger.log('cancel', 'agendamentos', self.agendamento_id, scheduling_ref.get().to_dict())
        return True