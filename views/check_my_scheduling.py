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
from utils.encrypt import encryptUser
from utils.client_storage import loadStoredUser, setSchedulingEdit
from utils import whatsapp
from utils.whatsapp import TELEFONE_CONTACT
from utils import scheduling_db

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        collaborator_ref,
        lista_agendamento,
        func1,
        func2,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.collaborator_ref = collaborator_ref
        self.lista_agendamentos = lista_agendamento
        self.func = func1
        self.func2 = func2
        
        self.dict_agendamentos = dict()
        self.data_table = createDataTable(True, ["Data/hora", "Status", "Nome do cliente", "Serviço agendado"])
        self.no_scheduling = createTitle("Não possui agendamentos", False)

        if len(self.lista_agendamentos) == 0:
            self.data_table.visible = False
            self.no_scheduling.visible = True
        
        else:
            self.data_table.visible = True
            self.no_scheduling.visible = False

            self.data_atual = datetime.datetime.now()
            self.data_formatada = self.data_atual.strftime("%d-%m-%Y")
            for agendamento in self.lista_agendamentos:
                agenda_id = agendamento.id
                agenda = agendamento.to_dict()
                data = agenda.get('data', 'N/A')
                if self.data_formatada > data:
                    continue
                if agenda['status_agendamento'] == "Em andamento":
                    data = agenda.get('data', 'N/A')
                    hora = agenda.get('horario', 'N/A')
                    data_hora = data + " as " + hora
                    self.data_table.content.controls[0].rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(data_hora, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ft.DataCell(ft.Text(agenda['status_agendamento'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ft.DataCell(ft.Text(agenda['nome'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ft.DataCell(ft.Text(agenda['nome_servico'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                    ], on_select_changed=lambda e, agenda=agenda, agenda_id=agenda_id: self.func2(agenda, agenda_id)))
                    self.dict_agendamentos[agenda_id] = agenda
                elif agenda['status_agendamento'] == "Concluido" or agenda['status_agendamento'] == "Cancelado":
                    data = agenda.get('data', 'N/A')
                    hora = agenda.get('horario', 'N/A')
                    data_hora = data + " as " + hora
                    self.data_table.content.controls[0].rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(data_hora, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ft.DataCell(ft.Text(agenda['status_agendamento'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ft.DataCell(ft.Text(agenda.get('nome', 'N/A'), text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                        ft.DataCell(ft.Text(agenda['nome_servico'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                    ]))
            if len(self.data_table.content.controls[0].rows) == 0:
                self.data_table.visible = False
                self.no_scheduling.visible = True

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
                createElevatedButton(self.btn_name, self.func),
            ],
        )
    
async def view_check_my_scheduling(page: ft.Page):
    
    stored_user = await loadStoredUser(page)
    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    
    data_scheduling = None
    collaborator_documents = dict()
    
    db = get_firestore_client()
    collaborator_ref = db.collection("colaborador").stream()

    agendamentos_ref = db.collection("agendamentos")
    query = agendamentos_ref.where(filter=FieldFilter("user_id", "==", stored_user['localId']))
    agendamentos = query.stream()
    
    lista_agendamentos = list(agendamentos)

    def sort_key(agendamento):
        agenda = agendamento.to_dict()
        status = agenda.get('status_agendamento', 'N/A')
        horario = agenda.get('horario', '23:59')
            
        # Prioriza agendamentos com horário e status "Em andamento"
        if 'horario' in agenda and status == "Em andamento":
            return (0, horario)
        # Agendamentos com horário e status "Concluido" vêm depois
        elif 'horario' in agenda and status == "Concluido":
            return (1, horario)
        # Agendamentos sem horário e com status "Concluido" vêm antes dos cancelados
        elif 'horario' not in agenda and status == "Concluido":
            return (2, horario)
        # Agendamentos cancelados vêm por último
        elif status == "Cancelado":
            return (3, horario)
        # Agendamentos sem horário e sem status "Em andamento" ou "Concluido" vêm por último
        else:
            return (4, horario)

    lista_agendamentos.sort(key=sort_key)

    # Obtendo o dicionario referente aos atendentes
    for collaborator in collaborator_ref:
        collaborator_id = collaborator.id
        collaborator_data = collaborator.to_dict()
        collaborator_documents[collaborator_id] = collaborator_data

    def show_details(row_data, id):
        nonlocal data_scheduling
        
        if data_scheduling is None:
            data_scheduling = {}
        data_scheduling.clear()
        data_scheduling[id] = row_data
        colaborador_id = row_data['colaborador_id']
        # dialog.content.controls = [flet.Text(f"{key}: {value}") for key, value in row_data.items()]
        dialog.content.controls = [
            ft.Text(f"Data: {row_data['data']}"),
            ft.Text(f"Hórario: {row_data['horario']}"),
            ft.Text(f"Nome: {row_data['nome']}"),
            ft.Text(f"Nome do atendente: {collaborator_documents[colaborador_id]['nome']}"),
            ft.Text(f"Telefone: {row_data['telefone']}"),
            ft.Text(f"Serviço: {row_data['nome_servico']}"),
            ft.Text(f"Preço: R${row_data['preco_servico']}"),
            ft.Text(f"Duração: {row_data['duracao_servico']} min"),
            ft.Text(f"Status: {row_data['status_agendamento']}"),
        ]
        dialog.open = True
        
        page.update()

    def close_dialog():
        dialog.open = False
        page.update()
    
    async def editar_agendamento(e):
        close_dialog()
        await asyncio.sleep(0.1)
        encrypt_scheduling = encryptUser(data_scheduling)
        await setSchedulingEdit(page, encrypt_scheduling)
        page.go('/editar-agendamento')
        
    # Função para abrir o CupertinoAlertDialog para confirmar cancelamento
    async def dismiss_cancel_dialog(e):
        cancel_dialog.open = False
        page.update()
        await asyncio.sleep(0.1)
        # page.dialog = dialog  # Redefine o dialog original
        # page.update()
        # close_dialog()
    
    async def cancelar_agendamento(e):
        id_scheduling = list(data_scheduling.keys())[0]
        dict_agendamento = _scheduling_.dict_agendamentos[id_scheduling]
        # Obtendo valores para enviar a mensagem no whatsapp
        _phone_user = dict_agendamento['telefone']
        _name_user = dict_agendamento['nome']
        _day_choose = dict_agendamento['data']
        _hour_choose = dict_agendamento['horario']
        _collaborator_choose = dict_agendamento['colaborador_id']
        _name_collaborator = collaborator_documents[_collaborator_choose]['nome']
        
        texto = "Agendamento cancelado!"

        type_message = "cancel"

        mensagem = whatsapp.MessageSender()
        mensagem_enviada = mensagem.send_message(_phone_user, _name_user,
                                                    _day_choose, _hour_choose,
                                                    _name_collaborator, type_message)
        mensagem_contato = mensagem.send_contact(_phone_user, TELEFONE_CONTACT)

        cancelar = scheduling_db.CancelScheduling(id_scheduling)
        _cancelar = cancelar.cancel_scheduling()
        cancel_dialog.open = False
        page.update()
        await asyncio.sleep(0.1)
        # page.dialog = dialog  # Redefine o dialog original
        # page.update()
        close_dialog()
        await asyncio.sleep(0.1)

        await transition.main(page, texto, None)

    async def open_cancel_dialog(e):
        global cancel_dialog
        cancel_dialog = ft.CupertinoAlertDialog(
            title=ft.Text("Atenção"),
            content=ft.Text("Você tem certeza que deseja cancelar o agendamento?"),
            actions=[
                ft.CupertinoDialogAction("Sim", is_destructive_action=True, on_click=cancelar_agendamento),
                ft.CupertinoDialogAction(text="Não", on_click=dismiss_cancel_dialog),
            ],
        )
        e.control.page.overlay.append(cancel_dialog)
        # e.control.page.dialog = cancel_dialog
        cancel_dialog.open = True
        e.control.page.update()

    # Configuração do dialog principal
    dialog = ft.AlertDialog(
        title=ft.Text("Detalhes do Agendamento"),
        scrollable=True,
        
        content=ft.Column([
            # Adicione aqui os detalhes do agendamento que você deseja exibir
        ]),
        actions=[
            ft.TextButton("Editar Agendamento", on_click=editar_agendamento),
            ft.TextButton("Cancelar Agendamento", on_click=open_cancel_dialog),
            ft.TextButton("Fechar", on_click=lambda _: close_dialog()),
        ],
    )

    page.overlay.append(dialog)
    # page.dialog = dialog

    async def back_button(e):
        page.go('/menu')

    _scheduling_ = UserWidget(
        "Meus agendamentos!",
        "Voltar",
        collaborator_ref,
        lista_agendamentos,
        back_button,
        show_details,
    )
    return _scheduling_

    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_scheduling_)

    view = ft.View(
        route='/verificar-meus-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )

    return view