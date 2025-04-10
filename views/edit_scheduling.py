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
from utils.client_storage import loadStoredUser, loadSchedulingEdit, removeSchedulingEdit
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
from utils import whatsapp
from utils.whatsapp import TELEFONE_CONTACT
from utils import scheduling_db

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        agendamento_id,
        agendamento_data,
        service_ref,
        func1,
        func2,
        func3,
        func4,
        func5
        ):
        super().__init__()
        self.title = title
        self.name = agendamento_data[agendamento_id]['nome']
        self.phone = agendamento_data[agendamento_id]['telefone']
        self.agendamento_id = agendamento_id
        self.agendamento_data = agendamento_data
        self.service_ref = service_ref
        self.func = func1
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        self.func5 = func5
        self.service_dict = {}

        self.data_objeto = datetime.datetime.strptime(agendamento_data[self.agendamento_id]['data'], '%d-%m-%Y')
        self.field_name_text = createInputTextField('Informe seu nome!', False, self.name, set_read_only=True)
        self.field_phone_text = createInputTextField('Informe seu telefone!', False, self.phone, set_read_only=True)
        self.service_choose = createDropdown("Escolha o Serviço", self.func5, set_value=self.agendamento_data[self.agendamento_id]['servico_id'])
        self.date_picker = createDatePickerForScheduling(self.func)
        self.day_choose = createCallDatePicker("Escolha o dia novamente", self.date_picker,set_visible=True)
        self.hour_choose = createDropdown("Escolha o Hórario", self.func2, False)
        self.collaborator_choose = createDropdown("Escolha o(a) atendente", None, False)
        self._register = createElevatedButton("Atualizar agendamento", self.func3)
        self._back_button = createElevatedButton("Voltar", self.func4)

        self.content = self.build()

        for _service in self.service_ref:
            # Cada documento é um objeto com ID e dados
            service = self.service_choose.content
            _service_id = _service.id
            _service_data = _service.to_dict()
            
            if _service_data['permitir_agendamento']:
        
                _nome = f'{_service_data["nome"]} - R${_service_data["preco"]}'
                #adiciona no dropdown o Servico
                service.options.append(ft.dropdown.Option(text= _nome, key= _service_id,))
                self.service_dict[_service_id] = _service_data

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                ft.Column(
                    spacing=12,
                    controls=[
                        self.field_name_text,
                        self.field_phone_text,
                    ],
                ),
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

async def view_edit_scheduling(page: ft.Page):
    
    stored_user = await loadStoredUser(page)
    stored_id = await loadSchedulingEdit(page)
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    
    if stored_id is None:
        page.go("/")
        view = ft.View()
        return view
    
    colaboradores_disponivel = {}
    horario_disponivel = []
    agendamento_data = dict()

    db = get_firestore_client()

    # Extraindo a chave e os dados do stored_id
    agendamento_id = list(stored_id.keys())[0]
    agendamento_data[agendamento_id] = stored_id[agendamento_id]

    # agendamento_ref = db.collection('agendamentos').document(agendamento_id).get()
    # agendamento_data = agendamento_ref.to_dict()
    
    async def _on_date_change(e=None):
        _scheduling_.hour_choose.visible = True
        _scheduling_.collaborator_choose.visible = True
        _scheduling_.update()
        hour_choose = _scheduling_.hour_choose.content
        collaborator_choose = _scheduling_.collaborator_choose.content
        hour_choose.value = None
        hour_choose.update()
        collaborator_choose.value = None
        collaborator_choose.update()
        selected_date = e.control.value if e else _scheduling_.date_picker.content.value
        data_formatada = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        await verifica_horario(data_formatada, agendamento_id)

    def _service_change(e):
        _scheduling_.day_choose.visible = True
        _scheduling_.day_choose.update()
        if _scheduling_.date_picker.content.value:
            _on_date_change()

    async def verifica_horario(data_formatada, agendamento_id=None):
        colaborador_documents = db.collection("colaborador").stream()
        service_choose = _scheduling_.service_choose.content
        service_dict = _scheduling_.service_dict[service_choose.value]

        hour_choose = _scheduling_.hour_choose.content
        hour_choose.options.clear()
        collaborator_choose = _scheduling_.collaborator_choose.content
        collaborator_choose.options.clear()

        duracao_servico = datetime.timedelta(minutes=service_dict['duracao'])
        
        data_atual = datetime.datetime.now()
        dia_atual = data_atual.day
        mes_atual = data_atual.month
        hora_atual = data_atual.strftime('%H:%M')
        
        colaboradores_disponivel.clear()
        horario_disponivel.clear()

        agendamentos = get_agendamentos(db, data_formatada)
        
        tasks = [processa_colaborador(colaborador, data_formatada, dia_atual, mes_atual, hora_atual, duracao_servico, agendamentos, colaboradores_disponivel, horario_disponivel, agendamento_id) for colaborador in colaborador_documents]
        await asyncio.gather(*tasks)
        
        hour_choose.options = [ft.dropdown.Option(hora) for hora in horario_disponivel] if colaboradores_disponivel else [ft.dropdown.Option("Não possui horário disponivel")]
        hour_choose.update()

    def verifica_colaborador(e):
        horario_escolhido = e.control.value
        collaborator_choose = _scheduling_.collaborator_choose.content
        collaborator_choose.options = [ft.dropdown.Option(text=dados['nome'], key=id) for id, dados in colaboradores_disponivel.items() if horario_escolhido in dados["horarios_disponivel"]]
        collaborator_choose.update()

    async def atualizar_agendamento(e):
        name_user = _scheduling_.field_name_text.content
        phone_user = _scheduling_.field_phone_text.content
        service_choose = _scheduling_.service_choose.content
        day_choose = _scheduling_.date_picker.content.value
        hour_choose = _scheduling_.hour_choose.content
        collaborator_choose = _scheduling_.collaborator_choose.content
        if checks_fields():
            service_dict = _scheduling_.service_dict[service_choose.value]
            day_choose = datetime.datetime.strptime(str(day_choose), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
            scheduling = scheduling_db.UpdateScheduling(agendamento_id, stored_user, name_user.value, phone_user.value, service_choose.value, day_choose, hour_choose.value, collaborator_choose.value, service_dict)
            _scheduling = scheduling.update_scheduling()

            name_collaborator = colaboradores_disponivel[collaborator_choose.value]['nome']
            type_message = "update"
            removeSchedulingEdit(page)
            mensagem = whatsapp.MessageSender()
            mensagem.send_message(phone_user.value, name_user.value, day_choose, hour_choose.value, name_collaborator, type_message)
            mensagem.send_contact(phone_user.value, TELEFONE_CONTACT)
            await asyncio.sleep(2.5)
            texto = "Agendamento atualizado!"
            await transition.main(page, texto, None)

    def checks_fields():
        name = _scheduling_.field_name_text
        phone =_scheduling_.field_phone_text
        service_choose = _scheduling_.service_choose
        hour_choose = _scheduling_.hour_choose
        collaborator_choose = _scheduling_.collaborator_choose
        fields = [
            (name, [length_validator(1, 100)]),
            (phone, [phone_with_ddd_validator]),
            (service_choose, [length_validator(1, 100)]),
            (hour_choose, [time_validator]),
            (collaborator_choose, [length_validator(1, 100)])
        ]
        return validate_fields(fields)

    async def _back_button(e):
        page.go('/menu')

    _scheduling_ = UserWidget(
        "Editar Agendamento!",
        agendamento_id,
        agendamento_data,
        db.collection("servico").stream(),
        _on_date_change,
        verifica_colaborador,
        atualizar_agendamento,
        _back_button,
        _service_change,
    )

    return _scheduling_
    
    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_scheduling_)

    view = ft.View(
        route='/editar-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )

    return view