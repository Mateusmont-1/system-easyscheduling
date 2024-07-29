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
from utils.client_storage import loadStoredUser, setServiceEdit
from utils.encrypt import encryptUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        service_ref,
        func1,
        func2,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.service_ref = service_ref
        self.func = func1
        self.func2 = func2

        self.data_table = createDataTable(list_columns=["Nome serviço", "Preço", "Duração"])
        self.no_scheduling = createTitle("Não possui serviços", False)
        # Itere sobre os resultados
        for servico_ in self.service_ref:
            servico_id = servico_.id
            servico = servico_.to_dict()

            self.data_table.content.controls[0].rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(servico['nome'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD,
                                            )),
                    ft.DataCell(ft.Text(servico['preco'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD)),
                    ft.DataCell(ft.Text(servico['duracao'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD)),
                ],
                on_select_changed=lambda e, _servico=servico, _servico_id =servico_id: self.func(_servico, _servico_id),
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
    
async def view_check_service(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    db = get_firestore_client()
    servico_ref = db.collection("servico").stream()
    
    def show_details(row_data, id):
        nonlocal data_service

        if data_service is None:
            data_service = {}
        data_service.clear()
        data_service[id] = row_data

        if row_data['permitir_agendamento']:
            texto = "Sim"
        else:
            texto = "Não"
        
        dialog.content.controls = [
            ft.Text(f"Nome Serviço: {row_data['nome']}"),
            ft.Text(f"Preço: {row_data['preco']}"),
            ft.Text(f"Permitir agendamento: {texto}"),
            ft.Text(f"Duração: {row_data['duracao']} min"),
        ]
        dialog.open = True
        
        page.update()

    async def button_editar_servico(e):
        close_dialog()
        await asyncio.sleep(0.1)
        print('teste')
        encrypt_service = encryptUser(data_service)
        await setServiceEdit(page, encrypt_service)
        page.go('/editar-servico')

    data_service = None
    # Criar o diálogo uma vez
    dialog = ft.AlertDialog(
        scrollable=True,
        title=ft.Text("Detalhes do Serviço"),
        content=ft.Column([]),
        actions=[
            ft.TextButton("Editar serviço", on_click=button_editar_servico),
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
        "Serviços!",
        "Voltar",
        servico_ref,
        show_details,
        back_button,
    )

    return _service_
    _service_main = createMainColumn(page)
    _service_main.content.controls.append(ft.Container(padding=0))
    _service_main.content.controls.append(_service_)

    return ft.View(
        route='/verificar-servicos',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _service_main,
        ]
    )