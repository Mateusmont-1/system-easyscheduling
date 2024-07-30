import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import register_expenses
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
    createCheckbox, createDataTable, createButtonWithVisibility
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO, COLOR_BORDER_COLOR
from utils.client_storage import loadStoredUser, loadExpenseEdit, removeExpenseEdit
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
from utils.validation import validate_fields, length_validator, converte_float

class UserWidget(ft.Container):
    def __init__(
            self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        category_ref,
        expense_ref,
        func,
        func2,
        ):
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.category_ref = category_ref
        self.id_expense = list(expense_ref.keys())[0]
        self.expense_ref = expense_ref[self.id_expense]
        self.func = func
        self.func2 = func2
        super().__init__()

        self.category_dict = dict()

        self.date_expense = self.expense_ref.get('data', '')
        self.categoria_id = self.expense_ref.get('categoria_id', '')
        self.valor_expense = str(self.expense_ref.get('valor', ''))
        self.descricao = self.expense_ref.get('descricao', '')

        self.field_date_expense = createInputTextField("Data despesa", set_visible=True, default_value=self.date_expense, set_read_only=True)
        self.field_price_text = createInputTextField("Valor (R$)", set_visible=True, default_value=self.valor_expense)
        self.field_description_text = createInputTextField("Descrição", set_visible=True, default_value=self.descricao)
        self.category_expense = createDropdown("Escolha a categoria", set_visible=True, set_value=self.categoria_id)

        for categoria in self.category_ref:
            # Cada documento é um objeto com ID e dados            
            category_dropdown = self.category_expense.content
            _categoria_id = categoria.id
            _categoria_data = categoria.to_dict()
            
            if _categoria_data['ativo']:
                _nome = _categoria_data['nome']
            
                # adiciona no dropdown as categoria de despesa
                category_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _categoria_id,))

                self.category_dict[_categoria_id] = _categoria_data

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
                        self.field_date_expense,
                    ],
                ),
                self.category_expense,
                ft.Column(
                    spacing=12,
                    controls=[
                        self.field_price_text,
                        self.field_description_text,
                    ],
                ),
                ft.Container(padding=5),
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func2),
                ft.Container(padding=10),
            ],
        )
    
async def view_edit_expense(page: ft.Page):
    stored_user = await loadStoredUser(page)
    stored_expense = await loadExpenseEdit(page)
    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    if stored_expense is None:
        page.go("/menu")
        view = ft.View()
        return view
    
    id_expense = list(stored_expense.keys())[0]

    # Obtém o cliente Firestore e a referência aos colaboradores
    db = get_firestore_client()
    category_ref = db.collection("categorias").stream()

    async def update_expense(e):
        
        verifica = checks_fields()
            
        if verifica:
            
            descricao = str(_expense_.field_description_text.content.value)
            preco = float(
                str(
                    _expense_.field_price_text.content.value
                    ).replace(',', ".")
                )
            id_category = _expense_.category_expense.content.value
            name_category = _expense_.category_dict[id_category]['nome']

            date = datetime.datetime.strptime(str(_expense_.date_expense), '%d-%m-%Y')
            ano_despesa = date.strftime('%Y')
            mes_despesa = date.strftime('%m')
            
            registra_despesa = register_expenses.UpdateExpense(id_expense,
                                                               mes_despesa,
                                                               ano_despesa,
                                                               id_category,
                                                               name_category,
                                                               preco,
                                                               descricao
                                                               )
            
            confirma = registra_despesa.atualizar_despesa()
            if confirma:
                await removeExpenseEdit(page)
                texto = "Despesa atualizada!"
                await transition.main(page, texto, None)
            else:
                print('Não foi cadastrado')

    def checks_fields():
        descricao = _expense_.field_description_text.content
        preco = _expense_.field_price_text.content
        dropdown_category = _expense_.category_expense.content
        
        verificar = 0
        if descricao.value == "":
            descricao.border_color = COLOR_BORDER_COLOR_ERROR
            descricao.update()
            verificar += 1
        else:
            descricao.border_color = COLOR_BORDER_COLOR
            descricao.update()
        if preco.value == "":
            preco.border_color = COLOR_BORDER_COLOR_ERROR
            preco.update()
            verificar += 1
        elif not converte_float(preco.value.replace(',', ".")):
            verificar += 1
            preco.border_color = COLOR_BORDER_COLOR_ERROR
            preco.update()
        elif float(preco.value.replace(',', ".")) == 0.0:
            verificar += 1
            preco.border_color = COLOR_BORDER_COLOR_ERROR
            preco.update()
        else:
            preco.border_color = COLOR_BORDER_COLOR
            preco.update()
        if dropdown_category.value == None:
            dropdown_category.border_color = COLOR_BORDER_COLOR_ERROR
            dropdown_category.update()
            verificar += 1
        else:
            dropdown_category.border_color = COLOR_BORDER_COLOR
            dropdown_category.update()
        
        descricao.update()
        preco.update()
        
        return True if verificar == 0 else None
    
    def converte_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    _expense_ = UserWidget(
        "Editar despesa!",
        "Entre com os dados da despesa abaixo",
        "Atualizar",
        "Voltar",
        category_ref,
        stored_expense,
        update_expense,
        back_button,
    )

    return _expense_
