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
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
    createDataTable
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO, COLOR_TEXT_IN_FIELD
from utils.client_storage import loadStoredUser, setCategoryEdit
from utils.encrypt import encryptUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        category_ref,
        func1,
        func2,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.category_ref = category_ref
        self.func = func1
        self.func2 = func2

        self.data_table = createDataTable(list_columns=["Nome categoria", "Ativo"])
        self.no_scheduling = createTitle("Não possui categoria", False)
        # Itere sobre os resultados
        for categoria_ in self.category_ref:
            categoria_id = categoria_.id
            categoria = categoria_.to_dict()

            if categoria['ativo']:
                texto = "Sim"
            else:
                texto = "Não"

            self.data_table.content.controls[0].rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(categoria['nome'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD,
                                            )),
                    ft.DataCell(ft.Text(texto,
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD)),
                ],
                    on_select_changed=lambda e, _categoria=categoria, _categoria_id =categoria_id: self.func(_categoria, _categoria_id)
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
    
async def view_check_category(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    db = get_firestore_client()
    category_ref = db.collection("categorias").stream()
    
    def show_details(row_data, id):
        nonlocal data_category

        if data_category is None:
            data_category = {}
        data_category.clear()
        data_category[id] = row_data

        if row_data['ativo']:
            texto = "Sim"
        else:
            texto = "Não"
        
        dialog.content.controls = [
            ft.Text(f"Nome Categoria: {row_data['nome']}"),
            ft.Text(f"Ativo: {texto}"),
        ]
        dialog.open = True
        
        page.update()

    async def button_edit_category(e):
        close_dialog()
        await asyncio.sleep(0.1)
        encrypt_category = encryptUser(data_category)
        await setCategoryEdit(page, encrypt_category)
        page.go('/editar-categoria')

    data_category = None
    # Criar o diálogo uma vez
    dialog = ft.AlertDialog(
        scrollable=True,
        title=ft.Text("Detalhes da categoria"),
        content=ft.Column([]),
        actions=[
            ft.TextButton("Editar categoria", on_click=button_edit_category),
            ft.TextButton("Fechar", on_click=lambda e: close_dialog()),
            
        ]
    )

    def close_dialog():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)
    # page.dialog = dialog
    
    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")


    _category_ = UserWidget(
        "Categorias!",
        "Voltar",
        category_ref,
        show_details,
        back_button,
    )

    return _category_
