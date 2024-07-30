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
from utils.client_storage import loadStoredUser, loadSchedulingEdit, removeSchedulingEdit
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
        func,
        func2,
        func3
        ):
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.category_ref = category_ref
        self.func = func
        self.func2 = func2
        self.func3 = func3
        super().__init__()

        self.category_dict = dict()

        self.field_price_text = createInputTextField("Valor (R$)", set_visible=False)
        self.field_description_text = createInputTextField("Descrição", set_visible=False)
        self.date_picker = createDatePickerForScheduling(self.func, set_days=31, set_days_before=31)
        self.day_choose = createCallDatePicker("Escolha o dia", self.date_picker, set_visible=True)
        self.category_expense = createDropdown("Escolha a categoria", set_visible=False)
        self.create_expense = createButtonWithVisibility(self.btn_name, visible=False, func=self.func2)

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
                self.day_choose,
                self.category_expense,
                ft.Column(
                    spacing=12,
                    controls=[
                        self.field_price_text,
                        self.field_description_text,
                    ],
                ),
                ft.Container(padding=5),
                self.create_expense,
                createElevatedButton(self.btn_name2, self.func3),
                ft.Container(padding=10),
                self.date_picker
            ],
        )
    
async def view_create_expense(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    # Obtém o cliente Firestore e a referência aos colaboradores
    db = get_firestore_client()
    category_ref = db.collection("categorias").stream()

    # Variáveis para armazenar a data formatada, ano e mês
    data_formatada = None
    data_ano = None
    data_mes = None

    # Função chamada quando a data é alterada
    def on_date_change(e=None):
        # Torna visíveis os campos relacionados à despesa
        _expense_.category_expense.visible = True
        # _expense_.category_expense.update()
        _expense_.field_description_text.content.visible = True
        # _expense_.field_description_text.update()
        _expense_.field_price_text.content.visible = True
        # _expense_.field_price_text.update()
        _expense_.create_expense.visible = True
        # _expense_.create_expense.content.update()
        _expense_.update()

        # Formata a data selecionada
        selected_date = e.control.value
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        nonlocal data_formatada, data_ano, data_mes
        data_formatada = data_objeto.strftime('%d-%m-%Y')
        data_ano = data_objeto.strftime('%Y')
        data_mes = data_objeto.strftime('%m')

    # Função para criar um novo produto
    async def create_expense(e):
        if verificar_campos():
            descricao = str(_expense_.field_description_text.content.value)
            preco = float(str(_expense_.field_price_text.content.value).replace(',', "."))
            id_category = _expense_.category_expense.content.value
            name_category = _expense_.category_dict[id_category]['nome']

            # Cria e registra a despesa
            registra_despesa = register_expenses.CreateExpense(data_formatada, data_mes, data_ano, id_category, name_category, preco, descricao)
            if registra_despesa.registrar_despesa():
                await transition.main(page, "Despesa registrada!", None)
            else:
                print('Não foi cadastrado')

    # Verifica se os campos estão preenchidos corretamente
    def verificar_campos():
        descricao = _expense_.field_description_text.content
        preco = _expense_.field_price_text.content
        dropdown_category = _expense_.category_expense.content

        # Função auxiliar para checar cada campo
        def check_field(field, error_condition):
            if error_condition:
                field.border_color = COLOR_BORDER_COLOR_ERROR
                field.update()
                return False
            field.border_color = COLOR_BORDER_COLOR
            field.update()
            return True

        # Verifica todos os campos
        valid = True
        valid &= check_field(descricao, descricao.value == "")
        valid &= check_field(preco, preco.value == "" or not converte_float(preco.value.replace(',', ".")) or float(preco.value.replace(',', ".")) == 0.0)
        valid &= check_field(dropdown_category, dropdown_category.value is None)
        return valid

    # Converte string para float
    def converte_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    # Cria o widget de adição de despesas
    _expense_ = UserWidget(
        "Adicionar despesa!",
        "Entre com os dados da despesa abaixo",
        "Cadastrar",
        "Voltar",
        category_ref,
        on_date_change,
        create_expense,
        back_button,
    )

    return _expense_
