import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import register_expenses
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
    createCheckbox
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO
from utils.client_storage import loadStoredUser, removeCategoryEdit , loadCategoryEdit
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
from utils.validation import validate_fields, length_validator, converte_float

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        category_ref,
        func,
        func2
        ):
        super().__init__()
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.category_id = list(category_ref.keys())[0]
        self.category_ref = category_ref[self.category_id]
        self.func = func
        self.func2 = func2

        self.field_name_text = createInputTextField("Nome", default_value=self.category_ref['nome'])
        self.field_checkbox = createCheckbox("Permitir agendamento?",set_value=self.category_ref['ativo'])
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
                    ],
                ),
                self.field_checkbox,         
                ft.Container(padding=5),
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func2),
                ft.Container(padding=10),
            ],
        )
    
async def view_edit_category(page: ft.Page):
    stored_user = await loadStoredUser(page)
    stored_category = await loadCategoryEdit(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    if stored_category is None:
        page.go("/menu")
        view = ft.View()
        return view
    
    id_category = list(stored_category.keys())[0]

    async def update_category(e):
            
        if checks_fields():
            nome = str(_category_.field_name_text.content.value)
            checkbox = _category_.field_checkbox.content.controls[0].value
            
            editar_produto = register_expenses.UpdateCategory(nome, checkbox, id_category)
            confirma = editar_produto.atualizar_categoria()
            if confirma:
                await removeCategoryEdit(page)
                texto = "Categoria atualizada!"
                await transition.main(page, texto, None)
                ...
            else:
                nome = _category_.field_name_text.content
                nome.error_text = "Este serviço já existe!"
                nome.update()

    def checks_fields():
        nome = _category_.field_name_text
        fields = [(nome, [length_validator(1, 100)]),]
        
        return validate_fields(fields)

    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    _category_ = UserWidget(
        "Atualizar categoria!",
        "Entre com os dados da categoria abaixo",
        "Atualizar",
        "Voltar",
        stored_category,
        update_category,
        back_button,
    )

    return _category_
