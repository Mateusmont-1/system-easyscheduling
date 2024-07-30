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
    createImageLogo, createDropdown, createDatePickerForReport, createCallDatePicker,
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
        func1,
        func2,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.func = func1
        self.func2 = func2
        
        self.collaborator_dict = dict()
        self.data_table = createDataTable(False, ["Categoria", "Valor (R$)"])
        self.date_picker = createDatePickerForReport(self.func)
        self.day_choose = createCallDatePicker("Escolha o mês", self.date_picker, set_visible=True)
        self.no_scheduling = createTitle("Não possui receitas", False)
        
        self.content = self.build()

    def build(self):
        return ft.Column(
            scroll="hidden",
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self.day_choose,
                ft.Container(padding=3),
                self.data_table,
                self.date_picker,
                self.no_scheduling,
                createElevatedButton(self.btn_name, self.func2),
            ],
        )
    
async def view_check_report_monthly(page: ft.Page):
    
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
    
    db = get_firestore_client()
    
    def _on_date_change(e=None):
        # Verifica se a função foi executada no date_picker
        if e:
            selected_date = e.control.value
        else:
            selected_date = _report_.date_picker.content.value

        # Obtendo referência ao widget data_table
        data_table = _report_.data_table.content
        data_table.controls[0].rows.clear()
        data_table.update()

        # Formatando a data para extrair mês e ano
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        mes = data_objeto.month
        ano = data_objeto.year

        # Query no banco de dados referente ao mês e ano
        transacoes_ref = db.collection("transacoes").document(str(ano)).collection(str(mes).zfill(2))
        despesas_ref = db.collection("despesas").document(str(ano)).collection(str(mes).zfill(2))

        transacoes = transacoes_ref.stream()
        despesas = despesas_ref.stream()

        lista_transacoes = list(transacoes)
        lista_despesas = list(despesas)

        total_ganho = 0
        total_despesas = 0

        # Itera sobre as transações para calcular o total de ganhos
        for transacao in lista_transacoes:
            transacao_data = transacao.to_dict()
            valor = transacao_data.get('total', 0)
            total_ganho += valor

        # Itera sobre as despesas para calcular o total de despesas
        for despesa in lista_despesas:
            despesa_data = despesa.to_dict()
            valor = despesa_data.get('valor', 0)
            total_despesas += valor

        saldo = total_ganho - total_despesas

        # Exibe o total de ganhos, despesas e saldo no mês selecionado
        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Total Ganho",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {total_ganho:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ]))
        data_table.update()

        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Total Despesas",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {total_despesas:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ]))
        data_table.update()

        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Saldo",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {saldo:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ]))
        data_table.update()

        # Atualiza a visibilidade da data_table
        if len(data_table.controls[0].rows) == 0:
            _report_.data_table.visible = False
            _report_.data_table.update()
            _report_.no_scheduling.visible = True
            _report_.no_scheduling.update()
        else:
            _report_.data_table.visible = True
            _report_.data_table.update()
            _report_.no_scheduling.visible = False
            _report_.no_scheduling.update()
    
    async def _back_button(e):
        page.go('/menu')

    _report_ = UserWidget(
        "Receitas colaborador!",
        "Voltar",
        _on_date_change,
        _back_button,
    )
    
    return _report_
    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_report_)

    view = ft.View(
        route='/verificar-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )

    return view