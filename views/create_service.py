import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import register_service
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
    createCheckbox
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO
from utils.client_storage import loadStoredUser, loadSchedulingEdit, removeSchedulingEdit
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
from utils.validation import validate_fields, length_validator, converte_float

class UserWidget(ft.Container):
    def __init__(
            self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        func,
        func2,
        ):
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.func = func
        self.func2 = func2
        super().__init__()

        self.field_name_text = createInputTextField("Nome")
        self.field_price_text = createInputTextField("Preço (R$)")
        self.field_time_text = createInputTextField("Duração (Minutos)", type="phone")
        self.field_checkbox = createCheckbox("Permitir agendamento?")
        self.content = self.build()
    
    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                createSubTitle(self.sub_title),
                ft.Column(
                    spacing=12,
                    controls=[
                        self.field_name_text,
                        self.field_price_text,
                        self.field_time_text,
                    ],
                ),
                self.field_checkbox,         
                ft.Container(padding=5),
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func2),
                ft.Container(padding=10),
            ],
        )
    
async def view_create_service(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    # Função para cadastrar o serviço
    async def create_service(e): 
        if checks_fields():
            nome = str(_service_.field_name_text.content.value)
            preco = float(str(_service_.field_price_text.content.value).replace(',', "."))
            duracao = int(_service_.field_time_text.content.value)
            checkbox_scheduling = _service_.field_checkbox.content.controls[0].value
            
            # Cria e cadastra o serviço
            cadastra_servico = register_service.Service(nome, preco, duracao, checkbox_scheduling)
            confirma = cadastra_servico.criar_servico()
            if confirma:
                texto = "Serviço cadastrado!"
                await transition.main(page, texto, None)
            else:
                nome = _service_.field_name_text.content
                nome.error_text = "Este serviço já existe!"
                nome.update()

    def checks_fields():
        nome = _service_.field_name_text
        preco = _service_.field_price_text
        duracao = _service_.field_time_text
        
        fields = [
            (nome, [length_validator(1, 100)]),
            (preco, [converte_float]),  # Usando converte_float da validation.py
            (duracao, [lambda v: v.isdigit()])  # Duração deve ser um número inteiro
        ]
        
        return validate_fields(fields)

    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    _service_ = UserWidget(
        "Adicionar serviço!",
        "Entre com os dados do serviço abaixo",
        "Cadastrar",
        "Voltar",
        create_service,
        back_button,
    )

    return _service_

    _service_main = createMainColumn(page)
    _service_main.content.controls.append(ft.Container(padding=0))
    _service_main.content.controls.append(_service_)

    return ft.View(
        route='/cadastrar-servico',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _service_main,
        ]
    )
