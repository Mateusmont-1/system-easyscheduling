import flet as ft
from functools import partial
from email_validator import validate_email, EmailNotValidError
import re

from utils.interface import (
    createTitle, createSubTitle, createRememberCheckbox, createElevatedButton, 
    createButtonForgotPassword, createFooterText, createInputTextField, createMainColumn,
    createCheckboxTerms, createDropdown, createCheckbox, createButtonWithVisibility
)
from utils.validation import (
    validate_fields, is_valid_email, length_validator, ddd_validator, phone_validator, checkbox_validator, min_length_validator,
)
from utils.config import (COLOR_BORDER_COLOR_ERROR,COLOR_BORDER_COLOR)
from utils.client_storage import setEmail
from utils import register
from utils import login
from views import transition
from utils.firebase_config import get_firestore_client
from utils.client_storage import loadStoredUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        type_collaboraty,
        func,
        func2,
        func3,
        func4,
        ):
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.type_collaborator_ref = type_collaboraty
        self.func = func
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        super().__init__()

        self.field_email_text = createInputTextField("E-mail")
        self.field_password_text = createInputTextField("Senha", True)
        self.field_name_text = createInputTextField("Nome")
        self.field_ddd_text = createInputTextField("DDD (Ex:11)", size=12, width_field=97.5, type="phone")
        self.field_phone_text = createInputTextField("Telefone", size=12, width_field=167.5, type="phone")
        self.field_start_day_week = createInputTextField("Começa (hh:mm)", size=13, width_field=145)
        self.field_end_day_week = createInputTextField("Termina (hh:mm)", size=13, width_field=145)
        self.field_start_saturday = createInputTextField("Começa (hh:mm)", size=13, width_field=145)
        self.field_end_saturday = createInputTextField("Termina (hh:mm)", size=13, width_field=145)
        self.field_start_sunday = createInputTextField("Começa (hh:mm)", size=13, width_field=145)
        self.field_end_sunday = createInputTextField("Termina (hh:mm)", size=13, width_field=145)

        self.type_collaborator = createDropdown("Escolha o nivel de acesso", self.func2)

        for type in self.type_collaborator_ref:
            # Cada documento é um objeto com ID e dados     
            if type.id != "cliente":
                type_dropdown = self.type_collaborator.content
                _type_id = type.id
                _type_data = type.to_dict()
                _nome = type.id
                # adiciona no dropdown o atendente
                type_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _type_id,))

        self.checkbox_collaborator = createCheckbox("Cadastrar como atendente ?", set_visible=False, set_func=self.func2)

        self.text = createSubTitle("Informe o horário de atendimento", False)
        self.text2 = createSubTitle("Segunda a Sexta-feira:", False)
        self.text3 = createSubTitle("Sábado:", False)
        self.text4 = createSubTitle("Domingo:", False)

        self.checkbox_schedulling = createCheckbox("Permitir agendamento", set_visible=False)
        self.checkbox_terms = createCheckboxTerms()

        self.weekdays_button = createButtonWithVisibility("Dias de trabalho", visible=False, func=self.func4)

        self.row_day_week = ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=False,
                    controls=[
                        self.field_start_day_week,
                        self.field_end_day_week
                        ],
                )
        
        self.row_saturday = ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=False,
                    controls=[
                        self.field_start_saturday,
                        self.field_end_saturday,
                        ],
                )
        
        self.row_sunday = ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=False,
                    controls=[
                        self.field_start_sunday,
                        self.field_end_sunday,
                        ],
                )

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
                        self.field_email_text,
                        self.field_password_text,
                        self.field_name_text,
                    ],
                ),
                ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=True,
                    controls=[
                        self.field_ddd_text,
                        self.field_phone_text,
                        ],
                ),
                self.type_collaborator,
                self.checkbox_collaborator,
                self.text,
                self.text2,
                self.row_day_week,
                self.text3,
                self.row_saturday,
                self.text4,
                self.row_sunday,
                self.checkbox_schedulling,
                self.checkbox_terms,
                ft.Container(padding=5),
                self.weekdays_button,
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func3),
                
            ],
        )
    
async def view_register_collaborator(page: ft.Page):

    stored_user = await loadStoredUser(page)

    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view

    # Estado inicial dos dias da semana
    work_monday = True
    work_tuesday = True
    work_wednesday = True
    work_thursday= True
    work_friday = True
    work_saturday = True
    work_sunday = True

    # Obtém referência ao Firestore
    db = get_firestore_client()
    type_collaboraty_ref = db.collection("funcoes").stream()

    # Função para abrir o diálogo de seleção dos dias da semana
    def open_weekday_dialog(e):
        weekdays_dialog = ft.AlertDialog(
            title=ft.Text("Selecione os Dias da Semana"),
            scrollable=True,
            content=ft.Column(
                controls=[
                    ft.Checkbox(label="Segunda-feira", value=work_monday, data="monday"),
                    ft.Checkbox(label="Terça-feira", value=work_tuesday, data="tuesday"),
                    ft.Checkbox(label="Quarta-feira", value=work_wednesday, data="wednesday"),
                    ft.Checkbox(label="Quinta-feira", value=work_thursday, data="thursday"),
                    ft.Checkbox(label="Sexta-feira", value=work_friday, data="friday"),
                    ft.Checkbox(label="Sábado", value=work_saturday, data="saturday"),
                    ft.Checkbox(label="Domingo", value=work_sunday, data="sunday"),
                ]
            ),
            actions=[ft.TextButton("OK", on_click=close_weekday_dialog)],
        )
        page.dialog = weekdays_dialog
        weekdays_dialog.open = True
        page.update()
    
    # Função para fechar o diálogo e atualizar o estado dos dias da semana
    def close_weekday_dialog(e):
        nonlocal work_monday, work_tuesday, work_wednesday, work_thursday, work_friday, work_saturday, work_sunday
        checkboxes = page.dialog.content.controls
        work_monday = checkboxes[0].value
        work_tuesday = checkboxes[1].value
        work_wednesday = checkboxes[2].value
        work_thursday = checkboxes[3].value
        work_friday = checkboxes[4].value
        work_saturday = checkboxes[5].value
        work_sunday = checkboxes[6].value
        page.dialog.open = False
        page.update()

    # Função assíncrona para registrar o colaborador
    async def _register_collaboraty(e):
        email, senha, nome, ddd, telefone, checkbox_termos, type_collaboraty, checkbox_create_collaborator, checkbox_scheduling, workday_start_time, workday_end_time, saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time = get_form_values()

        if verifica_campos():
            telefone_completo = f'({ddd}){telefone.replace("-", "")}'
            list_work_days = get_work_days()
            
            cadastro = create_collaborator(email, senha, nome, telefone_completo, checkbox_termos, type_collaboraty, checkbox_create_collaborator, list_work_days, checkbox_scheduling, workday_start_time, workday_end_time, saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time)
            
            if cadastro.uid:
                texto = "Colaborador cadastrado!"
                await transition.main(page, texto, None)
                print(f"Dias de trabalho selecionados: {list_work_days}")
            else:
                show_email_error(email)
        
    # Função para obter os valores do formulário
    def get_form_values():
        email = _collaborator_.field_email_text.content.value
        senha = _collaborator_.field_password_text.content.value
        nome = _collaborator_.field_name_text.content.value
        ddd = _collaborator_.field_ddd_text.content.value
        telefone = _collaborator_.field_phone_text.content.value
        checkbox_termos = _collaborator_.checkbox_terms.content.controls[0].controls[0].value
        type_collaboraty = _collaborator_.type_collaborator.content.value
        checkbox_create_collaborator = _collaborator_.checkbox_collaborator.content.controls[0].value
        checkbox_scheduling = _collaborator_.checkbox_schedulling.content.controls[0].value
        workday_start_time = _collaborator_.field_start_day_week.content.value
        workday_end_time = _collaborator_.field_end_day_week.content.value
        saturday_start_time = _collaborator_.field_start_saturday.content.value
        saturday_end_time = _collaborator_.field_end_saturday.content.value
        sunday_start_time = _collaborator_.field_start_sunday.content.value
        sunday_end_time = _collaborator_.field_end_sunday.content.value
        
        return email, senha, nome, ddd, telefone, checkbox_termos, type_collaboraty, checkbox_create_collaborator, checkbox_scheduling, workday_start_time, workday_end_time, saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time

    # Função para criar o colaborador
    def create_collaborator(email, senha, nome, telefone_completo, checkbox_termos, type_collaboraty, checkbox_create_collaborator, list_work_days, checkbox_scheduling, workday_start_time, workday_end_time, saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time):
        cadastro = register.Collaborator(
            email, senha, nome, telefone_completo,
            checkbox_termos, type_collaboraty, checkbox_create_collaborator,
            list_work_days, checkbox_scheduling, workday_start_time, workday_end_time,
            saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time
        )
        cadastro.criar_colaborador()
        return cadastro

    # Função para obter os dias de trabalho
    def get_work_days():
        work_days = []
        if work_monday:
            work_days.append(0)
        if work_tuesday:
            work_days.append(1)
        if work_wednesday:
            work_days.append(2)
        if work_thursday:
            work_days.append(3)
        if work_friday:
            work_days.append(4)
        if work_saturday:
            work_days.append(5)
        if work_sunday:
            work_days.append(6)
        return work_days

    # Função para mostrar erro no campo de email
    def show_email_error(email):
        email_input = _collaborator_.controls[0].controls[2].controls[0].content
        email_input.border_color = COLOR_BORDER_COLOR_ERROR
        email_input.value = "E-mail informado em uso"
        email_input.update()
            
    # Função para verificar os campos do formulário
    def verifica_campos():
        def is_valid_email(email):
            try:
                validate_email(email)  # Valida o email
                return True
            except EmailNotValidError as ex:
                print(str(ex))
                return False
        
        # Expressão regular para validar o formato "HH:MM"
        time_format_regex = re.compile(r'^\d{2}:\d{2}$')

        # Função para validar um campo de horário
        def validate_time_field(time_field):
            if time_field.value == "" or not time_format_regex.match(time_field.value):
                time_field.border_color = COLOR_BORDER_COLOR_ERROR
                time_field.update()
                return 1
            time_field.border_color = COLOR_BORDER_COLOR
            time_field.update()
            return 0

        # Obtém os valores dos campos do formulário
        # email = _register_collaboraty_.controls[0].controls[2].controls[0].content
        # senha = _register_collaboraty_.controls[0].controls[2].controls[1].content
        # nome = _register_collaboraty_.controls[0].controls[2].controls[2].content
        # ddd = _register_collaboraty_.controls[0].controls[3].controls[0].content
        # telefone = _register_collaboraty_.controls[0].controls[3].controls[1].content
        # type_collaboraty = _register_collaboraty_._type_collaborator.content
        # checkbox_create_collaborator = _register_collaboraty_._checkbox_collaborator.content.controls[0].value
        # checkbox_termos = _register_collaboraty_._checkbox_terms.content.controls[0].controls[0]

        email = _collaborator_.field_email_text.content
        senha = _collaborator_.field_password_text.content
        nome = _collaborator_.field_name_text.content
        ddd = _collaborator_.field_ddd_text.content
        telefone = _collaborator_.field_phone_text.content
        checkbox_termos = _collaborator_.checkbox_terms.content.controls[0].controls[0]
        type_collaboraty = _collaborator_.type_collaborator.content
        checkbox_create_collaborator = _collaborator_.checkbox_collaborator.content.controls[0].value
        

        verifica = 0
        # Validação do campo de email
        if email.value == "" or not is_valid_email(email.value):
            email.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            email.border_color = COLOR_BORDER_COLOR
        email.update()

        # Validação do campo de senha
        if senha.value == "" or len(senha.value) < 6:
            senha.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            senha.border_color = COLOR_BORDER_COLOR
        senha.update()

        # Validação do campo de nome
        if nome.value == "":
            nome.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            nome.border_color = COLOR_BORDER_COLOR
        nome.update()

        # Validação do campo de DDD
        if ddd.value == "" or len(ddd.value) != 2:
            ddd.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            ddd.border_color = COLOR_BORDER_COLOR
        ddd.update()

        # Validação do campo de telefone
        telefone_value = telefone.value.replace('-', "")
        if telefone.value == "" or len(telefone_value) < 8 or len(telefone_value) > 9:
            telefone.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            telefone.border_color = COLOR_BORDER_COLOR
        telefone.update()

        # Validação do tipo de colaborador
        if type_collaboraty.value is None:
            type_collaboraty.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            type_collaboraty.border_color = COLOR_BORDER_COLOR
        type_collaboraty.update()

        # Validação do checkbox de termos
        if not checkbox_termos.value:
            checkbox_termos.is_error = True
            verifica += 1
        else:
            checkbox_termos.is_error = False
        checkbox_termos.update()

        # Verifica se a opção de criar atendente no sistema está ativa
        if checkbox_create_collaborator:
            # Obtém referências aos campos de horário
            workday_start_time = _collaborator_.field_start_day_week.content
            workday_end_time = _collaborator_.field_end_day_week.content
            saturday_start_time = _collaborator_.field_start_saturday.content
            saturday_end_time = _collaborator_.field_end_saturday.content
            sunday_start_time = _collaborator_.field_start_sunday.content
            sunday_end_time = _collaborator_.field_end_sunday.content

            verifica += validate_time_field(workday_start_time)
            verifica += validate_time_field(workday_end_time)
            verifica += validate_time_field(saturday_start_time)
            verifica += validate_time_field(saturday_end_time)
            verifica += validate_time_field(sunday_start_time)
            verifica += validate_time_field(sunday_end_time)
        
        return verifica == 0

    # Função para checar se o colaborador pode ser criado
    def check_create_collaborator(e):
        type_collaboraty = _collaborator_.type_collaborator.content
        checkbox_create_collaborator = _collaborator_.checkbox_collaborator.content
        checkbox_scheduling = _collaborator_.checkbox_schedulling.content
        
        text_time = _collaborator_.text
        text_time2 = _collaborator_.text2
        text_time3 = _collaborator_.text3
        text_time4 = _collaborator_.text4

        row_segunda_sexta = _collaborator_.row_day_week
        row_sabado = _collaborator_.row_saturday
        row_domingo = _collaborator_.row_sunday
        work_day = _collaborator_.content.controls[16]
        
        if type_collaboraty.value == "administrador":
            checkbox_create_collaborator.visible = True
            checkbox_create_collaborator.update()
        else:
            checkbox_create_collaborator.visible = False
            checkbox_create_collaborator.controls[0].value = True
            checkbox_create_collaborator.update()
        
        elements = [
            checkbox_scheduling, text_time, text_time2, text_time3, text_time4,
            row_segunda_sexta, row_sabado, row_domingo, work_day
        ]
        visible = checkbox_create_collaborator.controls[0].value
        
        for element in elements:
            element.visible = visible
            element.update()

        
    # Função assíncrona para voltar à página principal
    async def back_button(e):
        page.go("/menu")
    
    # Cria o widget de registro de colaborador
    _collaborator_ = UserWidget(
        "Registrar colaborador!",
        "Entre com os dados do colaborador abaixo",
        "Registrar",
        "Voltar",
        type_collaboraty_ref,
        _register_collaboraty,
        check_create_collaborator,
        back_button,
        open_weekday_dialog,
    )

    return _collaborator_

    # Configuração do contêiner principal e adição do widget de registro
    _collaborator_main = createMainColumn(page)
    _collaborator_main.content.controls.append(ft.Container(padding=0))
    _collaborator_main.content.controls.append(_collaborator_)

    view = ft.View(
        route='/register_collaborator',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _collaborator_main,
        ]
    )

    return view