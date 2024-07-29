import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import login
from utils import register
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
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
        self.collaborator_documents = dict()

        self.collaborator_choose = createDropdown("Escolha o(a) atendente", func=self.func)

        for colaborador in self.collaborator_ref:
            # Cada documento é um objeto com ID e dados
            colaborador_dropdown = self.collaborator_choose.content
            _colaborador_id = colaborador.id
            _colaborador_data = colaborador.to_dict()
        
            _nome = _colaborador_data['nome']
            
            # adiciona no dropdown o atendente
            colaborador_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _colaborador_id,))

            self.collaborator_documents[_colaborador_id] = _colaborador_data

        self.day_off = createDataTable(visible=False,list_columns=["Dias de folga"])
        self.no_day_off = createTitle("Não possui folgas", False)
        

        self.content = self.build()

    
    def build(self):
        return ft.Column(
            scroll="hidden",
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self.collaborator_choose,
                ft.Container(padding=3),
                self.day_off,
                self.no_day_off,
                createElevatedButton(self.btn_name, self.func2)
            ],
        )
    
async def view_check_day_off(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    colaborador = None
    dia = None

    db = get_firestore_client()
    collaborator_ref = db.collection("colaborador").stream()
    
    async def _check_day_off(e=None):
        if e:
            collaborator_choose = e.control.value
        else:
            collaborator_choose = _day_off_.collaborator_choose.content.value
            collaborator_update = db.collection("colaborador").stream()
            documents = _day_off_.collaborator_documents
            documents.clear()
            for colaborador in collaborator_update:
                # Cada documento é um objeto com ID e dados
                _colaborador_id = colaborador.id
                _colaborador_data = colaborador.to_dict()

                documents[_colaborador_id] = _colaborador_data
        

        day_off_table = _day_off_.day_off
        no_day_off = _day_off_.no_day_off
        collaborator_ref = _day_off_.collaborator_documents[collaborator_choose]
        day_off_collaborator = collaborator_ref.get('dias_folga', False)
        if not day_off_collaborator:
            no_day_off.visible = True
            day_off_table.visible = False
        else:
            no_day_off.visible = False
            day_off_collaborator.sort()
            day_off_table.content.controls[0].rows.clear()
            current_date = datetime.datetime.now().date()
            for day in day_off_collaborator:
                day_date = datetime.datetime.strptime(day, "%d-%m-%Y").date()
                if day_date >= current_date:
                    day_off_table.visible = True
                    day_off_table.content.controls[0].rows.append(ft.DataRow(cells=[
                            ft.DataCell(ft.Text(day, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ], on_select_changed=lambda e,collaborator_choose=collaborator_choose ,collaborator_ref=collaborator_ref, day=day: show_details(collaborator_choose, collaborator_ref, day)))
            if len(day_off_table.content.controls[0].rows) == 0:
                no_day_off.visible = True
                day_off_table.visible = False
            
        no_day_off.update()
        day_off_table.update()
    
    def show_details(collaborator_choose, collaborator, day):
        nonlocal colaborador, dia
        dia = day
        colaborador = collaborator_choose
        cancel_dialog = ft.CupertinoAlertDialog(
            title=ft.Text("Atenção"),
            content=ft.Text(f"Você tem certeza que deseja cancelar a folga do dia {day} do colaborador {collaborator['nome']}?"),
            actions=[
                ft.CupertinoDialogAction("OK", is_destructive_action=True, on_click=cancelar_folga),
                ft.CupertinoDialogAction(text="Cancel", on_click=dismiss_cancel_dialog),
            ],
        )
        page.dialog = cancel_dialog
        page.dialog.open = True
        page.update()

    # Função para abrir o CupertinoAlertDialog para confirmar cancelamento
    async def dismiss_cancel_dialog(e=None):
        page.dialog.open = False
        page.update()
        await asyncio.sleep(0.1)
    
    async def cancelar_folga(e):
        cancel = register.CollaboratorLeaveCancellationManager(colaborador)
        confirma = cancel.cancelar_dia_folga(dia)
        await dismiss_cancel_dialog()
        await _check_day_off()

    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")


    _day_off_ = UserWidget(
        "Verificar folgas!!",
        "Voltar",
        collaborator_ref,
        _check_day_off,
        back_button,
    )

    return _day_off_
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