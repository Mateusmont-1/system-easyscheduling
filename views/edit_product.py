import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import register_product
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePicker, createCallDatePicker,
    createCheckbox
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO
from utils.client_storage import loadStoredUser, removeProductEdit , loadProductEdit
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
from utils.validation import validate_fields, length_validator, converte_float

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        product_ref,
        func,
        func2
        ):
        super().__init__()
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.product_id = list(product_ref.keys())[0]
        self.product_ref = product_ref[self.product_id]
        self.func = func
        self.func2 = func2

        self.field_name_text = createInputTextField("Nome", default_value=self.product_ref['nome'])
        self.field_price_text = createInputTextField("Preço (R$)", default_value=str(self.product_ref['preco']))
        self.field_checkbox = createCheckbox("Permitir agendamento?",set_value=self.product_ref['permitir_venda'])
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
                    ],
                ),
                self.field_checkbox,         
                ft.Container(padding=5),
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func2),
                ft.Container(padding=10),
            ],
        )
    
async def view_edit_product(page: ft.Page):
    stored_user = await loadStoredUser(page)
    stored_product = await loadProductEdit(page)
    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    if stored_product is None:
        page.go("/menu")
        view = ft.View()
        return view
    
    id_product = list(stored_product.keys())[0]

    async def update_service(e):
            
        if checks_fields():
            nome = str(_service_.field_name_text.content.value)
            preco = float(str(_service_.field_price_text.content.value).replace(',', "."))
            checkbox_sale = _service_.field_checkbox.content.controls[0].value
            
            editar_produto = register_product.UpdateProduct(nome, preco, checkbox_sale, id_product)
            confirma = editar_produto.atualizar_produto()
            if confirma:
                await removeProductEdit(page)
                texto = "Produto atualizado!"
                await transition.main(page, texto, None)
            else:
                nome = _service_.field_name_text.content
                nome.error_text = "Este produto já existe!"
                nome.update()

    def checks_fields():
        nome = _service_.field_name_text
        preco = _service_.field_price_text
        
        fields = [
            (nome, [length_validator(1, 100)]),
            (preco, [converte_float]),  # Usando converte_float da validation.py
        ]
        
        return validate_fields(fields)

    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    _service_ = UserWidget(
        "Editar produto!",
        "Entre com os dados do produto abaixo",
        "Atualizar",
        "Voltar",
        stored_product,
        update_service,
        back_button,
    )

    return _service_

    _service_main = createMainColumn(page)
    _service_main.content.controls.append(ft.Container(padding=0))
    _service_main.content.controls.append(_service_)

    return ft.View(
        route='/editar-produto',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _service_main,
        ]
    )
