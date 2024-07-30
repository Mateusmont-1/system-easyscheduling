import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createElevatedButton, 
     createDatePickerForScheduling, createCallDatePicker,
    createDataTable
)
from utils.client_storage import loadStoredUser, setExpenseEdit
from utils.encrypt import encryptUser
from utils.config import COLOR_TEXT_IN_FIELD

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        func1,
        func2,
        func3,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.func = func1
        self.func2 = func2
        self.func3 = func3

        self.date_picker = createDatePickerForScheduling(self.func2, set_days=15, set_days_before=30)
        self.day_choose = createCallDatePicker("Escolha o mês", self.date_picker, set_visible=True)
        self.data_table = createDataTable(list_columns=["Data", "Categoria", "Valor (R$)"], visible=False)
        self.no_scheduling = createTitle("Não possui despesas", False)
        
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
                createElevatedButton(self.btn_name, self.func3)
            ],
        )
    
async def view_check_expense(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    db = get_firestore_client()
    
    def _visible_button(e):
        dropdown = e.control.value
        _expense_.day_choose.visible = True
        _expense_.day_choose.update()

        if _expense_.date_picker.content.value != None:
            _on_date_change()

    def show_details(row_data, id):
        nonlocal data_expense
        
        dia, mes, ano = row_data['data'].split('-')
        mes_despesa = mes
        ano_despesa = ano

        if data_expense is None:
            data_expense = {}
        data_expense.clear()
        data_expense[id] = row_data

        dialog.content.controls = [
            ft.Text(f"Data: {row_data['data']}"),
            ft.Text(f"Categoria: {row_data['categoria_nome']}"),
            ft.Text(f"Valor: {row_data['valor']}"),
            ft.Text(f"Descrição: {row_data['descricao']}"),
        ]
        dialog.open = True
        
        page.update()

    async def button_edit_expense(e):
        close_dialog()
        await asyncio.sleep(0.1)
        encrypt_expense = encryptUser(data_expense)
        await setExpenseEdit(page, encrypt_expense)
        page.go('/editar-despesa')

    data_expense = None
    # Criar o diálogo uma vez
    dialog = ft.AlertDialog(
        scrollable=True,
        title=ft.Text("Detalhes da Despesa"),
        content=ft.Column([]),
        actions=[
            ft.TextButton("Editar despesa", on_click=button_edit_expense),
            ft.TextButton("Fechar", on_click=lambda e: close_dialog()),
            
        ]
    )

    def close_dialog():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)

    def despesas_por_mes_ano(ano, mes):
        despesas_filtradas = dict()

        # Referência à subcoleção do mês dentro do ano especificado
        mes_ref = db.collection('despesas').document(ano).collection(mes)
    
        # Consultar todas as despesas dentro do mês
        despesas = mes_ref.stream()
    
        for despesa in despesas:
            despesas_filtradas[despesa.id] = despesa.to_dict()
    
        return despesas_filtradas
    
    def _on_date_change(e=None):
        # verifica se a função foi executada no date_picker
        if e:
            selected_date = e.control.value
        else:
            selected_date = _expense_.date_picker.content.value
        
       # Obtendo referência ao widget data_table
        data_table = _expense_.data_table.content
        data_table.controls[0].rows.clear()
        data_table.update()
        
        # Formatando a data de "ano-mes-dia" para "mes/ano"
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        mes = data_objeto.strftime('%m')
        ano = data_objeto.strftime('%Y')
        
        # Consulta no banco de dados referente ao mês e ano selecionados
        despesas_filtradas = despesas_por_mes_ano(ano, mes)
        
        # Verifica se possui dados na lista
        if not despesas_filtradas:
            # Caso não possua, oculta a DataTable e aparece texto "Não possui despesas"
            _expense_.data_table.visible = False
            _expense_.data_table.update()
            _expense_.no_scheduling.visible = True
            _expense_.no_scheduling.update() 

        else:
            _expense_.data_table.visible = True
            _expense_.data_table.update()
            _expense_.no_scheduling.visible = False
            _expense_.no_scheduling.update()

            # Itera sobre os resultados
            for despesa_id, despesa_dict in despesas_filtradas.items():
                data = despesa_dict.get('data', 'N/A')
                valor = despesa_dict.get('valor', 'N/A')
                categoria = despesa_dict.get('categoria_nome', 'N/A')
                data_table.controls[0].rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(data, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                    ft.DataCell(ft.Text(categoria, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                    ft.DataCell(ft.Text(valor, text_align="center", weight="bold", color=COLOR_TEXT_IN_FIELD)),
                    ],
                    on_select_changed=lambda e, 
                    despesa_dict=despesa_dict, despesa_id=despesa_id: show_details(
                        despesa_dict, despesa_id)
                    )
                )
                data_table.update()

            if len(data_table.controls[0].rows) == 0:
                _expense_.data_table.visible = False
                _expense_.data_table.update()
                _expense_.no_scheduling.visible = True
                _expense_.no_scheduling.update()  
    
    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    
    _expense_ = UserWidget(
        "Verificar despesas!",
        "Voltar",
        _visible_button,
        _on_date_change,
        back_button,
    )

    return _expense_
