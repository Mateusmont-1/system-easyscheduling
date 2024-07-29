import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import login
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePicker, createCallDatePicker
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO
from utils.client_storage import loadStoredUser
from utils import whatsapp
from utils.whatsapp import TELEFONE_CONTACT
from utils import scheduling_db
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
# from utils.scheduling_utils import processa_colaborador

class UserWidget(ft.Container):
    def __init__(self, title, user_data, service_ref, on_date_change, on_service_change, on_register, on_back, on_collaborator_change):
        super().__init__()
        self.title = title
        self.user_data = user_data
        self.service_ref = service_ref
        self.on_date_change = on_date_change
        self.on_service_change = on_service_change
        self.on_register = on_register
        self.on_back = on_back
        self.on_collaborator_change = on_collaborator_change
        self.service_dict = {}

        self.field_name_text = createInputTextField("Informe seu nome", False, self.user_data.get('name', ''))
        self.field_number_text = createInputTextField("Informe seu numero", False, self.user_data.get('phone_number', ''), type="phone")
        self.service_choose = createDropdown("Escolha o Serviço", self.on_service_change)
        self.date_picker = createDatePicker(self.on_date_change)
        self.day_choose = createCallDatePicker("Escolha o dia", self.date_picker, set_visible=False)
        self.hour_choose = createDropdown("Escolha o Hórario", self.on_collaborator_change, False)
        self.collaborator_choose = createDropdown("Escolha o(a) atendente", None, False)
        self._register = createElevatedButton("Realizar agendamento", self.on_register)
        self._back_button = createElevatedButton("Voltar", self.on_back)

        self.content = self.build()

        for service in self.service_ref:
            service_data = service.to_dict()
            if service_data['permitir_agendamento']:
                service_id = service.id
                service_name = f'{service_data["nome"]} - R${service_data["preco"]}'
                self.service_choose.content.options.append(ft.dropdown.Option(text=service_name, key=service_id))
                self.service_dict[service_id] = service_data

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                ft.Column(spacing=12, controls=[self.field_name_text, self.field_number_text]),
                self.service_choose,
                self.day_choose,
                self.hour_choose,
                self.collaborator_choose,
                ft.Container(padding=3),
                self._register,
                self._back_button,
                self.date_picker,
            ],
        )

async def view_create_scheduling(page: ft.Page):
    stored_user = await loadStoredUser(page)
    if stored_user is None:
        page.go("/")
        return ft.View()

    db = get_firestore_client()
    service_ref = db.collection("servico").stream()
    colaboradores_disponivel = {}
    horario_disponivel = []

    async def on_date_change(e=None):
        _scheduling_.hour_choose.visible = True
        _scheduling_.collaborator_choose.visible = True
        _scheduling_.update()
        await verifica_horario(e)

    def _service_change(e):
        _scheduling_.day_choose.visible = True
        _scheduling_.day_choose.update()
        if _scheduling_.date_picker.content.value:
            on_date_change()

    async def verifica_horario(e=None):
        selected_date = e.control.value if e else _scheduling_.date_picker.content.value
        data_formatada = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        
        service_choose = _scheduling_.service_choose.content
        service_dict = _scheduling_.service_dict[service_choose.value]

        duracao_servico = datetime.timedelta(minutes=service_dict['duracao'])
        data_atual = datetime.datetime.now()
        dia_atual, mes_atual, hora_atual = data_atual.day, data_atual.month, data_atual.strftime('%H:%M')

        agendamentos = get_agendamentos(db, data_formatada)

        tasks = [
            processa_colaborador(colaborador, data_formatada, dia_atual, mes_atual, hora_atual, duracao_servico, agendamentos, colaboradores_disponivel, horario_disponivel)
            for colaborador in db.collection("colaborador").stream()
        ]
        await asyncio.gather(*tasks)
        update_dropdown_options()

    def update_dropdown_options():
        hour_choose = _scheduling_.hour_choose.content
        hour_choose.options = [ft.dropdown.Option(hora) for hora in horario_disponivel] if colaboradores_disponivel else [ft.dropdown.Option("Não possui horário disponivel")]
        hour_choose.update()

    def verifica_colaborador(e):
        horario_escolhido = e.control.value
        collaborator_choose = _scheduling_.collaborator_choose.content
        collaborator_choose.options = [ft.dropdown.Option(text=dados['nome'], key=id) for id, dados in colaboradores_disponivel.items() if horario_escolhido in dados["horarios_disponivel"]]
        collaborator_choose.update()

    async def agendar_corte(e):
        if checks_fields():
            name_user = _scheduling_.field_name_text.content
            phone_user = _scheduling_.field_number_text.content
            service_choose = _scheduling_.service_choose.content
            day_choose = _scheduling_.date_picker.content.value
            hour_choose = _scheduling_.hour_choose.content
            collaborator_choose = _scheduling_.collaborator_choose.content

            service_dict = _scheduling_.service_dict[service_choose.value]
            formatted_date = datetime.datetime.strptime(str(day_choose), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')

            scheduling = scheduling_db.Scheduling(stored_user, name_user.value, phone_user.value, service_choose.value, formatted_date, hour_choose.value, collaborator_choose.value, service_dict)
            _scheduling = scheduling.create_scheduling()

            name_collaborator = colaboradores_disponivel[collaborator_choose.value]['nome']
            mensagem = whatsapp.MessageSender()
            mensagem.send_message(phone_user.value, name_user.value, formatted_date, hour_choose.value, name_collaborator, "novo_agendamento")
            mensagem.send_contact(phone_user.value, TELEFONE_CONTACT)
            await asyncio.sleep(2.5)
            await transition.main(page, "Agendamento realizado!", None)

    def checks_fields():
        fields = [
            (_scheduling_.field_name_text, [length_validator(1, 100)]),
            (_scheduling_.field_number_text, [phone_with_ddd_validator]),
            (_scheduling_.service_choose, [length_validator(1, 100)]),
            (_scheduling_.hour_choose, [time_validator]),
            (_scheduling_.collaborator_choose, [length_validator(1, 100)])
        ]
        return validate_fields(fields)

    async def back_button(e):
        page.go('/menu')

    _scheduling_ = UserWidget(
        "Agendamento!",
        stored_user,
        service_ref,
        on_date_change,
        _service_change,
        agendar_corte,
        back_button,
        verifica_colaborador,
    )

    return _scheduling_

    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_scheduling_)

    return ft.View(
        route='/criar-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )


# Importante: Siga o mesmo padrão para a função view_edit_scheduling e qualquer outra lógica de negócio ou interface.


# import flet as ft
# from google.cloud.firestore_v1 import FieldFilter
# import asyncio
# import datetime

# from views import transition
# from utils import login
# from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
# from utils.firebase_config import get_firestore_client
# from utils.interface import (
#     createTitle, createSubTitle, createElevatedButton, 
#     createFooterText, createInputTextField, createMainColumn,
#     createImageLogo, createDropdown, createDatePicker, createCallDatePicker
# )
# from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO
# from utils.client_storage import loadStoredUser
# from utils import whatsapp
# from utils.whatsapp import TELEFONE_CONTACT
# from utils import scheduling_db
# # from utils.scheduling_utils import processa_colaborador

# class UserWidget(ft.Container):
#     def __init__(
#         self,
#         title:str,
#         user,
#         service_ref,
#         func1,
#         func2,
#         func3,
#         func4,
#         func5
#         ):
#         self.title = title
#         self.user = user
#         self.service_ref = service_ref
#         self.func = func1
#         self.func2 = func2
#         self.func3 = func3
#         self.func4 = func4
#         self.func5 = func5
#         self.service_dict = {}
#         super().__init__()

#         self.field_name_text = createInputTextField("Informe seu nome", False, self.user.get('name', ''))
#         self.field_number_text = createInputTextField("Informe seu numero", False, self.user.get('phone_number', ''), type="phone")
#         self.service_choose = createDropdown("Escolha o Serviço", self.func5)
#         self.date_picker = createDatePicker(self.func)
#         self.day_choose = createCallDatePicker("Escolha o dia", self.date_picker,set_visible=False)
#         self.hour_choose = createDropdown("Escolha o Hórario", self.func2, False)
#         self.collaborator_choose = createDropdown("Escolha o(a) atendente", None, False)
#         self._register = createElevatedButton("Realiazar agendamento", self.func3)
#         self._back_button = createElevatedButton("Voltar", self.func4)

#         self.content = self.build()

#         for _service in self.service_ref:
#             # Cada documento é um objeto com ID e dados
#             service = self.service_choose.content
#             _service_id = _service.id
#             _service_data = _service.to_dict()
            
#             if _service_data['permitir_agendamento']:
        
#                 _nome = f'{_service_data["nome"]} - R${_service_data["preco"]}'
#                 #adiciona no dropdown o Servico
#                 service.options.append(ft.dropdown.Option(text= _nome, key= _service_id,))
#                 self.service_dict[_service_id] = _service_data

#     def build(self):
#         return ft.Column(
#             horizontal_alignment="center",
#             controls=[
#                 createTitle(self.title),
#                 ft.Column(
#                     spacing=12,
#                     controls=[
#                         self.field_name_text,
#                         self.field_number_text,
#                     ],
#                 ),
#                 self.service_choose,
#                 self.day_choose,
#                 self.hour_choose,
#                 self.collaborator_choose,
#                 ft.Container(padding=3),
#                 self._register,
#                 self._back_button,
#                 self.date_picker,
#             ],
#         )
    
# async def view_create_scheduling(page: ft.Page):
    
#     stored_user = await loadStoredUser(page)
#     # Se não possuir user armazenado retorna para tela home
#     if stored_user is None:
#         page.go("/")
#         view = ft.View()
#         return view
    
#     #Criando variaveis
#     colaboradores_disponivel = {}
#     horario_disponivel = []
#     db = get_firestore_client()

#     async def _on_date_change(e=None):
#         _scheduling_.hour_choose.visible = True
#         _scheduling_.collaborator_choose.visible = True
#         _scheduling_.update()
#         hour_choose = _scheduling_.hour_choose.content
#         collaborator_choose = _scheduling_.collaborator_choose.content
#         hour_choose.value = None
#         hour_choose.update()
#         collaborator_choose.value = None
#         collaborator_choose.update()
#         selected_date = e.control.value if e else _scheduling_.date_picker.content.value
#         data_formatada = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
#         await verifica_horario(data_formatada)

#     def _service_change(e):
#         _scheduling_.day_choose.visible = True
#         _scheduling_.day_choose.update()
#         if _scheduling_.date_picker.content.value:
#             _on_date_change()

#     def string_to_time(time_str):
#         return datetime.datetime.strptime(time_str, '%H:%M')

#     def get_agendamentos(data_desejada):
#         agendamentos_ref = db.collection('agendamentos')
#         query = agendamentos_ref.where(
#                     filter=FieldFilter('data', "==", data_desejada)
#                 ).where(
#                     filter=FieldFilter('status_agendamento', 'in', ['Concluido', 'Em andamento'])
#                 ).stream()
        
#         agendamentos = {}
#         for agendamento in query:
#             agendamento_data = agendamento.to_dict()
#             colaborador_id = agendamento_data['colaborador_id']
#             if colaborador_id not in agendamentos:
#                 agendamentos[colaborador_id] = []
#             agendamentos[colaborador_id].append(agendamento_data)
        
#         return agendamentos

#     def periodo_disponivel(inicio, fim, agendamentos):
#         for agendamento_data in agendamentos:
#             horario_agendado_str = agendamento_data.get('horario')
#             if horario_agendado_str:
#                 horario_agendado = string_to_time(horario_agendado_str)
#                 duracao_agendada = datetime.timedelta(minutes=int(agendamento_data['duracao_servico']))
#                 fim_agendado = horario_agendado + duracao_agendada
#                 if inicio < fim_agendado and fim > horario_agendado:
#                     return False
#         return True

#     async def processa_colaborador(colaborador, data_formatada, dia_atual, mes_atual, hora_atual, duracao_servico, agendamentos):
#         dados = colaborador.to_dict()
#         dias_folga = dados.get('dias_folga', [])  
#         dias_trabalhados = dados.get('dias_trabalhados', [0, 1, 2, 3, 4, 5, 6])
#         if dados['permitir_agendamento'] and data_formatada not in dias_folga:
#             id = colaborador.id
#             dia, mes, ano = map(int, data_formatada.split("-"))
#             data = datetime.date(year=ano, month=mes, day=dia)
#             dia_semana = data.weekday()
#             if dia_semana not in dias_trabalhados:
#                 return

#             horarios_disponiveis = dados['dias_uteis'] if dia_semana < 5 else dados['sabado'] if dia_semana == 5 else dados['domingo']
#             for hora in horarios_disponiveis:
#                 if len(horarios_disponiveis) <= 1 or (dia == dia_atual and mes == mes_atual and hora < hora_atual):
#                     continue

#                 inicio_servico = string_to_time(hora)
#                 fim_servico = inicio_servico + duracao_servico
#                 if periodo_disponivel(inicio_servico, fim_servico, agendamentos.get(id, [])):
#                     if id not in colaboradores_disponivel:
#                         colaboradores_disponivel[id] = {"nome": dados["nome"], "horarios_disponivel": []}
#                     colaboradores_disponivel[id]["horarios_disponivel"].append(hora)
#                     if hora not in horario_disponivel:
#                         horario_disponivel.append(hora)
#                         horario_disponivel.sort()

#     async def verifica_horario(data_formatada):
#         colaborador_documents = db.collection("colaborador").stream()
#         service_choose = _scheduling_.service_choose.content
#         service_dict = _scheduling_.service_dict[service_choose.value]

#         hour_choose = _scheduling_.hour_choose.content
#         hour_choose.options.clear()
#         collaborator_choose = _scheduling_.collaborator_choose.content
#         collaborator_choose.options.clear()

#         duracao_servico = datetime.timedelta(minutes=service_dict['duracao'])
        
#         data_atual = datetime.datetime.now()
#         dia_atual = data_atual.day
#         mes_atual = data_atual.month
#         hora_atual = data_atual.strftime('%H:%M')
        
#         colaboradores_disponivel.clear()
#         horario_disponivel.clear()

#         agendamentos = get_agendamentos(data_formatada)
        
#         tasks = [processa_colaborador(colaborador, data_formatada, dia_atual, mes_atual, hora_atual, duracao_servico, agendamentos) for colaborador in colaborador_documents]
#         await asyncio.gather(*tasks)
        
#         hour_choose.options = [ft.dropdown.Option(hora) for hora in horario_disponivel] if colaboradores_disponivel else [ft.dropdown.Option("Não possui horário disponivel")]
#         hour_choose.update()

#     def verifica_colaborador(e):
#         horario_escolhido = e.control.value
#         collaborator_choose = _scheduling_.collaborator_choose.content
#         collaborator_choose.options = [ft.dropdown.Option(text=dados['nome'], key=id) for id, dados in colaboradores_disponivel.items() if horario_escolhido in dados["horarios_disponivel"]]
#         collaborator_choose.update()

#     async def agendar_corte(e):
#         print('Oi')
#         name_user = _scheduling_.field_name_text.content
#         phone_user = _scheduling_.field_number_text.content
#         service_choose = _scheduling_.service_choose.content
#         day_choose = _scheduling_.date_picker.content.value
#         hour_choose = _scheduling_.hour_choose.content
#         collaborator_choose = _scheduling_.collaborator_choose.content
#         if checks_fields():
#             service_dict = _scheduling_.service_dict[service_choose.value]
#             day_choose = datetime.datetime.strptime(str(day_choose), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')

#             scheduling = scheduling_db.Scheduling(stored_user, name_user.value, phone_user.value, service_choose.value, day_choose, hour_choose.value, collaborator_choose.value, service_dict)
#             _scheduling = scheduling.create_scheduling()

#             name_collaborator = colaboradores_disponivel[collaborator_choose.value]['nome']
#             type_message = "novo_agendamento"

#             mensagem = whatsapp.MessageSender()
#             mensagem.send_message(phone_user.value, name_user.value, day_choose, hour_choose.value, name_collaborator, type_message)
#             mensagem.send_contact(phone_user.value, TELEFONE_CONTACT)
#             await asyncio.sleep(2.5)
#             texto = "Agendamento realizado!"
#             await transition.main(page, texto, None)

#     def checks_fields():
#         name = _scheduling_.field_name_text
#         phone =_scheduling_.field_number_text
#         service_choose = _scheduling_.service_choose
#         hour_choose = _scheduling_.hour_choose
#         collaborator_choose = _scheduling_.collaborator_choose
#         fields = [
#             (name, [length_validator(1, 100)]),
#             (phone, [phone_with_ddd_validator]),
#             (service_choose, [length_validator(1, 100)]),
#             (hour_choose, [time_validator]),
#             (collaborator_choose, [length_validator(1, 100)])
#         ]
#         return validate_fields(fields)

#     async def _back_button(e):
#         page.go('/menu')

#     _scheduling_ = UserWidget(
#         "Agendamento!",
#         stored_user,
#         db.collection("servico").stream(),
#         _on_date_change,
#         verifica_colaborador,
#         agendar_corte,
#         _back_button,
#         _service_change,
#     )
    
#     _scheduling_main = createMainColumn(page)
#     _scheduling_main.content.controls.append(ft.Container(padding=0))
#     _scheduling_main.content.controls.append(_scheduling_)

#     view = ft.View(
#         route='/criar-agendamento',
#         horizontal_alignment="center",
#         vertical_alignment="center",
#         controls=[
#             _scheduling_main,
#         ]
#     )

#     return view