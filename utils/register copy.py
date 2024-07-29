from firebase_admin import db
from firebase_admin import auth
from firebase_admin import exceptions
from google.cloud import firestore
import requests
from datetime import datetime, timedelta

import firebase_admin.functions
from .logger import logger
from .firebase_config import get_firestore_client

db = get_firestore_client()

class User:
    def __init__(self, email:str, senha:str, nome:str, telefone:str,checkbox_termos:bool, tipo_usuario="cliente"):
        self.email = email
        self.senha = senha
        self.nome = nome
        self.telefone = telefone
        self.checkbox_termos = checkbox_termos
        self.user_data = {}
        self.uid = ""
        self.tipo_usuario = tipo_usuario

    def criar_usuario(self):
        try:
            user = auth.create_user(email=self.email, password=self.senha)
            doc_ref = db.collection('usuarios').document(user.uid)
            doc_ref.set({
                'email': self.email,
                'nome': self.nome,
                'telefone': self.telefone,
                'funcaoID': self.tipo_usuario,
                'terms_accepted': self.checkbox_termos,
                'terms_accepted_at': datetime.now()
            })
            self.uid = user.uid
            self.user_data = doc_ref.get().to_dict()
            logger.log('create', 'usuarios', user.uid, self.user_data)
            return self.user_data
        except exceptions.AlreadyExistsError:
            logger.log('error', 'usuarios', '', {'message': 'User already exists'})
            return None

class Collaborator:
    def __init__(
        self, email: str,
        senha: str,
        nome: str,
        telefone: str,
        checkbox_termos: bool,
        tipo_usuario,
        create_colaborador,
        list_work_days,
        scheduling=None,
        workday_start_time: str = None,
        workday_end_time: str = None,
        saturday_start_time: str = None,
        saturday_end_time: str = None,
        sunday_start_time: str = None,
        sunday_end_time: str = None,
    ):
        self.email = email
        self.senha = senha
        self.nome = nome
        self.telefone = telefone
        self.checkbox_termos = checkbox_termos
        self.tipo_usuario = tipo_usuario
        self.create_colaborador = create_colaborador
        self.list_work_days = list_work_days
        self.scheduling = scheduling
        if self.create_colaborador:
            self.workday_start_time = datetime.strptime(workday_start_time, "%H:%M")
            self.workday_end_time = datetime.strptime(workday_end_time, "%H:%M")
            self.saturday_start_time = datetime.strptime(saturday_start_time, "%H:%M")
            self.saturday_end_time = datetime.strptime(saturday_end_time, "%H:%M")
            self.sunday_start_time = datetime.strptime(sunday_start_time, "%H:%M")
            self.sunday_end_time = datetime.strptime(sunday_end_time, "%H:%M")

        self.user_data = {}
        self.uid = ""
        self.schedules_workday = list()
        self.schedules_saturday = list()
        self.schedules_sunday = list()

    def criar_colaborador(self):
        try:
            user = auth.create_user(email=self.email, password=self.senha)
            doc_ref = db.collection('usuarios').document(user.uid)
            doc_ref.set({
                'email': self.email,
                'nome': self.nome,
                'telefone': self.telefone,
                'funcaoID': self.tipo_usuario,
                'terms_accepted': self.checkbox_termos,
                'terms_accepted_at': datetime.now()
            })

            if self.create_colaborador:
                self._create_schedule(self.workday_start_time, self.workday_end_time, self.schedules_workday)
                self._create_schedule(self.saturday_start_time, self.saturday_end_time, self.schedules_saturday)
                self._create_schedule(self.sunday_start_time, self.sunday_end_time, self.schedules_sunday)

                colaborador_ref = db.collection('colaborador').document(user.uid)
                colaborador_ref.set({
                    'nome': self.nome,
                    'dias_uteis': self.schedules_workday,
                    'sabado': self.schedules_saturday,
                    'domingo': self.schedules_sunday,
                    'dias_trabalhados': self.list_work_days,
                    'permitir_agendamento': self.scheduling,
                    'semana_inicio': self.workday_start_time.strftime("%H:%M"),
                    'semana_fim': self.workday_end_time.strftime("%H:%M"),
                    'sabado_inicio': self.saturday_start_time.strftime("%H:%M"),
                    'sabado_fim': self.saturday_end_time.strftime("%H:%M"),
                    'domingo_inicio': self.sunday_start_time.strftime("%H:%M"),
                    'domingo_fim': self.sunday_end_time.strftime("%H:%M")
                })

            self.uid = user.uid
            self.user_data = doc_ref.get().to_dict()
            logger.log('create', 'colaborador', user.uid, self.user_data)
            return self.user_data
        except exceptions.AlreadyExistsError:
            logger.log('error', 'colaborador', '', {'message': 'Collaborator already exists'})
            return None

    def _create_schedule(self, start_time, end_time, schedule_list):
        current_time = start_time
        while current_time <= end_time:
            schedule_list.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=15)

class UpdateCollaborator:
    def __init__(
        self, 
        nome: str,
        telefone: str,
        tipo_usuario,
        scheduling,
        workday_start_time: str,
        workday_end_time: str,
        saturday_start_time: str,
        saturday_end_time: str,
        sunday_start_time: str,
        sunday_end_time: str,
        id_colaborador,
        list_work_days,
    ):
        self.nome = nome
        self.telefone = telefone
        self.tipo_usuario = tipo_usuario
        self.scheduling = scheduling
        self.workday_start_time = datetime.strptime(workday_start_time, "%H:%M")
        self.workday_end_time = datetime.strptime(workday_end_time, "%H:%M")
        self.saturday_start_time = datetime.strptime(saturday_start_time, "%H:%M")
        self.saturday_end_time = datetime.strptime(saturday_end_time, "%H:%M")
        self.sunday_start_time = datetime.strptime(sunday_start_time, "%H:%M")
        self.sunday_end_time = datetime.strptime(sunday_end_time, "%H:%M")
        self.id_colaborador = id_colaborador
        self.list_work_days = list_work_days
        self.user_data = {}
        self.schedules_workday = list()
        self.schedules_saturday = list()
        self.schedules_sunday = list()
        
    def atualizar_colaborador(self):
        try:
            doc_ref = db.collection('usuarios').document(self.id_colaborador)
            doc_ref.update({
                'nome': self.nome,
                'telefone': self.telefone,
                'funcaoID': self.tipo_usuario
            })

            self._create_schedule(self.workday_start_time, self.workday_end_time, self.schedules_workday)
            self._create_schedule(self.saturday_start_time, self.saturday_end_time, self.schedules_saturday)
            self._create_schedule(self.sunday_start_time, self.sunday_end_time, self.schedules_sunday)
                    
            colaborador_ref = db.collection('colaborador').document(self.id_colaborador)
            colaborador_ref.update({
                'nome': self.nome,
                'dias_uteis': self.schedules_workday,
                'sabado': self.schedules_saturday,
                'domingo': self.schedules_sunday,
                'dias_trabalhados': self.list_work_days,
                'permitir_agendamento': self.scheduling,
                'semana_inicio': self.workday_start_time.strftime("%H:%M"),
                'semana_fim': self.workday_end_time.strftime("%H:%M"),
                'sabado_inicio': self.saturday_start_time.strftime("%H:%M"),
                'sabado_fim': self.saturday_end_time.strftime("%H:%M"),
                'domingo_inicio': self.sunday_start_time.strftime("%H:%M"),
                'domingo_fim': self.sunday_end_time.strftime("%H:%M")
            })
                
            self.user_data = doc_ref.get().to_dict()
            logger.log('update', 'colaborador', self.id_colaborador, self.user_data)
            return self.user_data
        except exceptions.AlreadyExistsError:
            logger.log('error', 'colaborador', self.id_colaborador, {'message': 'Collaborator update failed'})
            return None
    
    def _create_schedule(self, start_time, end_time, schedule_list):
        current_time = start_time
        while current_time <= end_time:
            schedule_list.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=15)

class CollaboratorLeaveManager:
    def __init__(self, collaborator_id):
        self.collaborator_id = collaborator_id
        self.db = db

    def adicionar_datas_folga(self, datas_folga):
        try:
            doc_ref = self.db.collection('colaborador').document(self.collaborator_id)
            colaborador = doc_ref.get()
            
            if colaborador.exists:
                dados = colaborador.to_dict()
                dias_folga_atuais = dados.get('dias_folga', [])

                novas_datas = [data for data in datas_folga if data not in dias_folga_atuais]

                if not novas_datas:
                    return False

                doc_ref.update({"dias_folga": firestore.ArrayUnion(novas_datas)})
                logger.log('create', 'folgas', self.collaborator_id, novas_datas)
                return True
            else:
                return False
        except Exception as e:
            logger.log('error', 'folgas', self.collaborator_id, {'message': str(e)})
            return False

class CollaboratorLeaveCancellationManager:
    def __init__(self, collaborator_id):
        self.collaborator_id = collaborator_id
        self.db = db

    def cancelar_dia_folga(self, dia_folga):
        try:
            doc_ref = self.db.collection('colaborador').document(self.collaborator_id)
            colaborador = doc_ref.get()
            
            if colaborador.exists:
                dados = colaborador.to_dict()
                dias_folga_atuais = dados.get('dias_folga', [])

                if dia_folga in dias_folga_atuais:
                    dias_folga_atuais.remove(dia_folga)
                    doc_ref.update({"dias_folga": dias_folga_atuais})
                    logger.log('delete', 'folgas', self.collaborator_id, {'data': dia_folga})
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.log('error', 'folgas', self.collaborator_id, {'message': str(e)})
            return False

# Exemplo de uso da função
# novo_usuario = User('teste5@teste.com', '12345678', "11-48214286", "Mateus")
# novo_usuario.criar_usuario()
# if novo_usuario.uid:
#     print('Usuário criado com sucesso:', novo_usuario.uid)