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
from utils.client_storage import loadStoredUser, setCollaboratorEdit
from utils.encrypt import encryptUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        collaborator_ref,
        func1,
        func2,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.collaborator_ref = collaborator_ref
        self.func = func1
        self.func2 = func2

        self.data_table = createDataTable(list_columns=["Nome colaborador", "Permitir agendamento"])
        self.no_scheduling = createTitle("Não possui colaborador", False)

        for colaborador_ in self.collaborator_ref:
            colaborador_id = colaborador_.id
            colaborador = colaborador_.to_dict()
            if colaborador['permitir_agendamento']:
                texto = "Sim"
            else:
                texto = "Não"
            self.data_table.content.controls[0].rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(colaborador['nome'],
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD,
                                            )),
                    ft.DataCell(ft.Text(texto,
                                            text_align="center",
                                            weight="bold",
                                            color=COLOR_TEXT_IN_FIELD)),
                ],
                    on_select_changed=lambda e, _colaborador=colaborador, _colaborador_id =colaborador_id: self.func(_colaborador, _colaborador_id)
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
    
async def view_check_collaborator(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    db = get_firestore_client()
    collaborator_ref = db.collection("colaborador").stream()
    
    def show_details(row_data, id):
        nonlocal data_collaborator

        if data_collaborator is None:
            data_collaborator = {}
        data_collaborator.clear()
        data_collaborator[id] = row_data

        if row_data['permitir_agendamento']:
            texto = "Sim"
        else:
            texto = "Não"

        last_time1 = len(row_data['dias_uteis'])
        last_time2 = len(row_data['sabado'])
        last_time3 = len(row_data['domingo'])

        dialog.content.controls = [
            ft.Text(f"Nome Colaborador: {row_data['nome']}"),
            ft.Text(f"Permitir agendamento: {texto}"),
            ft.Text(f"Segunda a Sexta: {row_data['dias_uteis'][0]} as {row_data['dias_uteis'][last_time1-1]}"),
            ft.Text(f"Sábado: {row_data['sabado'][0]} as {row_data['sabado'][last_time2-1]}"),
            ft.Text(f"Domingo: {row_data['domingo'][0]} as {row_data['domingo'][last_time3-1]}"),
        ]
        dialog.open = True
        
        page.update()

    async def button_edit_collaborator(e):
        close_dialog()
        await asyncio.sleep(0.1)
        encrypt_collaborator = encryptUser(data_collaborator)
        await setCollaboratorEdit(page, encrypt_collaborator)
        page.go('/editar-colaborador')

    data_collaborator = None
    # Criar o diálogo uma vez
    dialog = ft.AlertDialog(
        scrollable=True,
        title=ft.Text("Detalhes do Colaborador"),
        content=ft.Column([]),
        actions=[
            ft.TextButton("Editar colaborador", on_click=button_edit_collaborator),
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


    _collaborator_ = UserWidget(
        "Colaboradores!",
        "Voltar",
        collaborator_ref,
        show_details,
        back_button,
    )

    return _collaborator_
    _service_main = createMainColumn(page)
    _service_main.content.controls.append(ft.Container(padding=0))
    _service_main.content.controls.append(_collaborator_)

    return ft.View(
        route='/verificar-servicos',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _service_main,
        ]
    )