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
from utils.encrypt import encryptUser
from utils.client_storage import loadStoredUser, setSchedulingFinish
from utils import whatsapp
from utils.whatsapp import TELEFONE_CONTACT
from utils import scheduling_db

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        collaborator_ref,
        func1,
        func2,
        func3
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.collaborator_ref = collaborator_ref
        self.func = func1
        self.func2 = func2
        self.func3 = func3
        
        self.collaborator_documents = dict()
        self.collaborator_choose = createDropdown("Escolha o(a) atendente", self.func)
        self.data_table = createDataTable(False, ["Data/hora", "Status", "Nome do cliente", "Serviço agendado"])
        self.date_picker = createDatePicker(self.func2)
        self.day_choose = createCallDatePicker("Escolha o dia", self.date_picker)
        self.no_scheduling = createTitle("Não possui agendamentos", False)


        for colaborador in self.collaborator_ref:
            # Cada documento é um objeto com ID e dados
            colaborador_dropdown = self.collaborator_choose.content
            _colaborador_id = colaborador.id
            _colaborador_data = colaborador.to_dict()
        
            _nome = _colaborador_data['nome']
            
            # adiciona no dropdown o atendente
            colaborador_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _colaborador_id,))

            self.collaborator_documents[_colaborador_id] = _colaborador_data
        
        self.content = self.build()

    def build(self):
        return ft.Column(
            scroll="hidden",
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self.collaborator_choose,
                self.day_choose,
                ft.Container(padding=3),
                self.data_table,
                self.date_picker,
                self.no_scheduling,
                createElevatedButton(self.btn_name, self.func3),
            ],
        )
    
async def view_check_scheduling(page: ft.Page):
    
    stored_user = await loadStoredUser(page)
    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    elif stored_user['funcaoID'] == "cliente":
        page.go("/menu")
        view = ft.View()
        return view

    data_scheduling = ""
    dict_agendamento = dict()
    
    db = get_firestore_client()
    collaborator_ref = db.collection("colaborador").stream()
    
    async def _visible_button(e):
        dropdown = e.control.value
        _scheduling_.day_choose.visible = True
        _scheduling_.day_choose.update()

        if _scheduling_.date_picker.content.value != None:
            await _on_date_change()
    
    def show_details(row_data, id):
        nonlocal data_scheduling
        
        if data_scheduling is None:
            data_scheduling = {}
        data_scheduling.clear()
        data_scheduling[id] = row_data
        print(data_scheduling)
        # dialog.content.controls = [flet.Text(f"{key}: {value}") for key, value in row_data.items()]
        dialog.content.controls = [
            ft.Text(f"Data: {row_data['data']}"),
            ft.Text(f"Hórario: {row_data['horario']}"),
            ft.Text(f"Nome: {row_data['nome']}"),
            ft.Text(f"Telefone: {row_data['telefone']}"),
            ft.Text(f"Serviço: {row_data['nome_servico']}"),
            ft.Text(f"Preço: R${row_data['preco_servico']}"),
            ft.Text(f"Duração: {row_data['duracao_servico']} min"),
            ft.Text(f"Status: {row_data['status_agendamento']}"),
        ]
        dialog.open = True
        page.update()

    data_scheduling = None

    def close_dialog():
        dialog.open = False
        page.update()

    # Função para finalizar o agendamento
    async def tela_finalizar(e):
        close_dialog()
        await asyncio.sleep(0.1)
        encrypt_scheduling = encryptUser(data_scheduling)
        await setSchedulingFinish(page, encrypt_scheduling)
        page.go('/finalizar-agendamento')

    # Função para fechar o CupertinoAlertDialog
    async def dismiss_cancel_dialog(e):
        cancel_dialog.open = False
        page.update()
        await asyncio.sleep(0.1)
    
    async def cancelar_agendamento(e):
        id_scheduling = list(data_scheduling.keys())[0]
        _dict_agendamento = dict_agendamento[id_scheduling]
        # Obtendo valores para enviar a mensagem no whatsapp
        _phone_user = _dict_agendamento['telefone']
        _name_user = _dict_agendamento['nome']
        _day_choose = _dict_agendamento['data']
        _hour_choose = _dict_agendamento['horario']
        _collaborator_choose = _dict_agendamento['colaborador_id']
        _name_collaborator = _scheduling_.collaborator_documents[_collaborator_choose]['nome']
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
        close_dialog()

        await _on_date_change()

    # Função para abrir o CupertinoAlertDialog
    def open_cancel_dialog(e):
        global cancel_dialog
        cancel_dialog = ft.CupertinoAlertDialog(
            title=ft.Text("Atenção"),
            content=ft.Text("Você tem certeza que deseja cancelar o agendamento?"),
            actions=[
                ft.CupertinoDialogAction("OK", is_destructive_action=True, on_click=cancelar_agendamento),
                ft.CupertinoDialogAction(text="Cancel", on_click=dismiss_cancel_dialog),
            ],
        )
        e.control.page.overlay.append(cancel_dialog)
        cancel_dialog.open = True
        e.control.page.update()

    # Configuração do dialog principal
    dialog = ft.AlertDialog(
        scrollable=True,
        title=ft.Text("Detalhes do Agendamento"),
        content=ft.Column([
            # Adicione aqui os detalhes do agendamento que você deseja exibir
        ]),
        actions=[
            ft.TextButton("Finalizar Agendamento", on_click=tela_finalizar),
            ft.TextButton("Cancelar Agendamento", on_click=open_cancel_dialog),
            ft.TextButton("Fechar", on_click=lambda _: close_dialog()),
        ],
    )

    page.overlay.append(dialog)

    async def _on_date_change(e=None):
        selected_date = e.control.value if e else _scheduling_.date_picker.content.value
        collaborator_choose = _scheduling_.collaborator_choose.content
        data_table = _scheduling_.data_table.content
        data_table.controls[0].rows.clear()
        await data_table.update_async()

        data_formatada = format_date(selected_date)
        lista_agendamentos = await fetch_scheduling_data(data_formatada, collaborator_choose.value)
        lista_agendamentos.sort(key=sort_scheduling_data)

        if lista_agendamentos:
            await update_data_table(lista_agendamentos, data_table)
        else:
            await display_no_scheduling()

    def format_date(selected_date):
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        return data_objeto.strftime('%d-%m-%Y')

    async def fetch_scheduling_data(data_formatada, collaborator_id):
        agendamentos_ref = db.collection("agendamentos")
        query = agendamentos_ref.where(filter=FieldFilter('data', '==', data_formatada)
                                    ).where(filter=FieldFilter("colaborador_id", "==", collaborator_id))
        agendamentos = query.stream()
        return list(agendamentos)

    def sort_scheduling_data(agendamento):
        agenda = agendamento.to_dict()
        status = agenda.get('status_agendamento', 'N/A')
        horario = agenda.get('horario', '23:59')

        if 'horario' in agenda and status == "Em andamento":
            return (0, horario)
        elif 'horario' in agenda and status == "Concluido":
            return (1, horario)
        elif 'horario' not in agenda and status == "Concluido":
            return (2, horario)
        elif status == "Cancelado":
            return (3, horario)
        else:
            return (4, horario)

    async def update_data_table(lista_agendamentos, data_table):
        _scheduling_.data_table.visible = True
        await _scheduling_.data_table.update_async()
        _scheduling_.no_scheduling.visible = False
        await _scheduling_.no_scheduling.update_async()

        for agendamento in lista_agendamentos:
            agenda_id = agendamento.id
            agenda = agendamento.to_dict()
            await append_scheduling_row(agenda, agenda_id, data_table)

        if not data_table.controls[0].rows:
            await display_no_scheduling()

    async def append_scheduling_row(agenda, agenda_id, data_table):
        data = agenda.get('data', 'N/A')
        hora = agenda.get('horario', 'N/A')
        nome_servico = agenda.get('nome_servico', False)

        if not nome_servico:
            servicos = agenda.get('servicos', [])
            if servicos and isinstance(servicos, list) and servicos:
                nome_servico = servicos[0].get('nome', 'N/A')
            else:
                nome_servico = 'N/A'

        data_hora = data + " as " + hora
        row = ft.DataRow(cells=[
            ft.DataCell(ft.Text(data_hora, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(agenda['status_agendamento'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(agenda['nome'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(nome_servico, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
        ])

        if agenda['status_agendamento'] == "Em andamento":
            row.on_select_changed = lambda e, agenda=agenda, agenda_id=agenda_id: show_details(agenda, agenda_id)

        data_table.controls[0].rows.append(row)
        dict_agendamento[agenda_id] = agenda
        await data_table.update_async()

    async def display_no_scheduling():
        _scheduling_.data_table.visible = False
        await _scheduling_.data_table.update_async()
        _scheduling_.no_scheduling.visible = True
        await _scheduling_.no_scheduling.update_async()

    # async def _on_date_change(e=None):
    #     if e:
    #         selected_date = e.control.value
    #     else:
    #         selected_date = _scheduling_.date_picker.content.value
        
    #     collaborator_choose = _scheduling_.collaborator_choose.content
    #     data_table = _scheduling_.data_table.content
    #     data_table.controls[0].rows.clear()
    #     await data_table.update_async()

    #     data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
    #     data_formatada = data_objeto.strftime('%d-%m-%Y')
        
    #     agendamentos_ref = db.collection("agendamentos")
    #     query = agendamentos_ref.where(filter=FieldFilter('data', '==', data_formatada)
    #                                 ).where(filter=FieldFilter("colaborador_id", "==", collaborator_choose.value))
    #     agendamentos = query.stream()
        
    #     lista_agendamentos = list(agendamentos)

    #     def sort_key(agendamento):
    #         agenda = agendamento.to_dict()
    #         status = agenda.get('status_agendamento', 'N/A')
    #         horario = agenda.get('horario', '23:59')
            
    #          # Prioriza agendamentos com horário e status "Em andamento"
    #         if 'horario' in agenda and status == "Em andamento":
    #             return (0, horario)
    #         # Agendamentos com horário e status "Concluido" vêm depois
    #         elif 'horario' in agenda and status == "Concluido":
    #             return (1, horario)
    #         # Agendamentos sem horário e com status "Concluido" vêm antes dos cancelados
    #         elif 'horario' not in agenda and status == "Concluido":
    #             return (2, horario)
    #         # Agendamentos cancelados vêm por último
    #         elif status == "Cancelado":
    #             return (3, horario)
    #         # Agendamentos sem horário e sem status "Em andamento" ou "Concluido" vêm por último
    #         else:
    #             return (4, horario)


    #     lista_agendamentos.sort(key=sort_key)

    #     if len(lista_agendamentos) != 0:
    #         _scheduling_.data_table.visible = True
    #         await _scheduling_.data_table.update_async()
    #         _scheduling_.no_scheduling.visible = False
    #         await _scheduling_.no_scheduling.update_async()
    #         for agendamento in lista_agendamentos:
    #             agenda_id = agendamento.id
    #             agenda = agendamento.to_dict()
    #             if agenda['status_agendamento'] == "Em andamento":
    #                 data = agenda.get('data', 'N/A')
    #                 hora = agenda.get('horario', 'N/A')
    #                 data_hora = data + " as " + hora
    #                 data_table.controls[0].rows.append(ft.DataRow(cells=[
    #                     ft.DataCell(ft.Text(data_hora, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                     ft.DataCell(ft.Text(agenda['status_agendamento'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                     ft.DataCell(ft.Text(agenda['nome'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                     ft.DataCell(ft.Text(agenda['nome_servico'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                 ], on_select_changed=lambda e, agenda=agenda, agenda_id=agenda_id: show_details(agenda, agenda_id)))
    #                 dict_agendamento[agenda_id] = agenda
    #                 await data_table.update_async()
    #             elif agenda['status_agendamento'] == "Concluido" or agenda['status_agendamento'] == "Cancelado":
    #                 data = agenda.get('data', 'N/A')
    #                 hora = agenda.get('horario', 'N/A')
    #                 nome_servico = agenda.get('nome_servico', False)
                    
    #                 # Verifica se 'nome_servico' não existe e busca no primeiro item do array 'servicos'
    #                 if not nome_servico:
    #                     servicos = agenda.get('servicos', [])
    #                     if servicos and isinstance(servicos, list) and len(servicos) > 0:
    #                         nome_servico = servicos[0].get('nome', 'N/A')
    #                     else:
    #                         nome_servico = 'N/A'
                    
    #                 data_hora = data + " as " + hora
    #                 data_table.controls[0].rows.append(ft.DataRow(cells=[
    #                     ft.DataCell(ft.Text(data_hora, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                     ft.DataCell(ft.Text(agenda['status_agendamento'], text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                     ft.DataCell(ft.Text(agenda.get('nome', 'N/A'), text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                     ft.DataCell(ft.Text(nome_servico, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
    #                 ]))
    #                 await data_table.update_async()
    #         if len(data_table.controls[0].rows) == 0:
    #             _scheduling_.data_table.visible = False
    #             await _scheduling_.data_table.update_async()
    #             _scheduling_.no_scheduling.visible = True
    #             await _scheduling_.no_scheduling.update_async()
    #     else:
    #         _scheduling_.data_table.visible = False
    #         await _scheduling_.data_table.update_async()
    #         _scheduling_.no_scheduling.visible = True
    #         await _scheduling_.no_scheduling.update_async()
    
    async def _back_button(e):
        page.go('/menu')

    _scheduling_ = UserWidget(
        "Verificar agendamentos!",
        "Voltar",
        collaborator_ref,
        _visible_button,
        _on_date_change,
        _back_button,
    )
    
    return _scheduling_
    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_scheduling_)

    view = ft.View(
        route='/verificar-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )

    return view