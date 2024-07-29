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
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker
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
        self.date_picker = createDatePickerForScheduling(self.on_date_change)
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
