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
    createImageLogo, createDropdown, createDatePicker, createCallDatePicker,
    createDataTable
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO, COLOR_TEXT_IN_FIELD
from utils.client_storage import loadStoredUser, setProductEdit
from utils.encrypt import encryptUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        produto_ref,
        func1,
        func2,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.product_ref = produto_ref
        self.func = func1
        self.func2 = func2

        self.data_table = createDataTable(list_columns=["Nome produto", "Preço", "Permitir venda"])
        self.no_scheduling = createTitle("Não possui produtos", False)
        # Itere sobre os resultados
        for product_ in self.product_ref:
            product_id = product_.id
            product = product_.to_dict()
            if product['permitir_venda']:
                texto = "Sim"
            else:
                texto = "Não"
            self.data_table.content.controls[0].rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(product['nome'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD,
                                            )),
                    ft.DataCell(ft.Text(product['preco'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD)),
                    ft.DataCell(ft.Text(texto,
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD)),
                ],
                on_select_changed=lambda e, _product=product, _product_id =product_id: self.func(_product, _product_id),
            ))
        
        if len(self.data_table.content.controls[0].rows) == 0:
            self.no_scheduling.visible = True
            self.data_table.visible = False

        self.content = self.build()

    
    def build(self):
        return ft.Column(
            scroll="hidden",
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                ft.Container(padding=3),
                self.data_table,
                self.no_scheduling,
                createElevatedButton(self.btn_name, self.func2)
            ],
        )
    
async def view_check_product(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    db = get_firestore_client()
    product_ref = db.collection("produto").stream()
    
    def show_details(row_data, id):
        nonlocal data_product

        if data_product is None:
            data_product = {}
        data_product.clear()
        data_product[id] = row_data

        if row_data['permitir_venda']:
            texto = "Sim"
        else:
            texto = "Não"
        
        dialog.content.controls = [
            ft.Text(f"Nome Produto: {row_data['nome']}"),
            ft.Text(f"Preço: {row_data['preco']}"),
            ft.Text(f"Permitir venda: {texto}"),
        ]
        dialog.open = True
        
        page.update()

    async def button_edit_product(e):
        close_dialog()
        await asyncio.sleep(0.1)
        encrypt_service = encryptUser(data_product)
        await setProductEdit(page, encrypt_service)
        page.go('/editar-produto')

    data_product = None
    # Criar o diálogo uma vez
    dialog = ft.AlertDialog(
        scrollable=True,
        title=ft.Text("Detalhes do Produto"),
        content=ft.Column([]),
        actions=[
            ft.TextButton("Editar produto", on_click=button_edit_product),
            ft.TextButton("Fechar", on_click=lambda e: close_dialog()),
            
        ]
    )

    def close_dialog():
        dialog.open = False
        page.update()

    page.dialog = dialog
    
    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")


    _service_ = UserWidget(
        "Produtos!",
        "Voltar",
        product_ref,
        show_details,
        back_button,
    )

    return _service_

    _service_main = createMainColumn(page)
    _service_main.content.controls.append(ft.Container(padding=0))
    _service_main.content.controls.append(_service_)

    return ft.View(
        route='/verificar-produtos',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _service_main,
        ]
    )