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
from utils.client_storage import loadStoredUser, loadCollaboratorEdit, removeCollaboratorEdit

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        type_collaboraty,
        user_ref,
        collaborator_ref,
        func,
        func2,
        func3,
        ):
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.type_collaborator_ref = type_collaboraty
        self.user_ref = user_ref.to_dict()
        self.collaborator_ref = collaborator_ref
        self.func = func
        self.func2 = func2
        self.func3 = func3
        super().__init__()

        self.field_name_text = createInputTextField("Nome", default_value=self.user_ref['nome'])
        self.field_phone_text = createInputTextField("Telefone", default_value=self.user_ref['telefone'], type="phone")
        self.field_start_day_week = createInputTextField("Começa (hh:mm)",
                                                         default_value=str(self.collaborator_ref['semana_inicio']), 
                                                         size=13, width_field=145)
        self.field_end_day_week = createInputTextField("Termina (hh:mm)",
                                                       default_value=str(self.collaborator_ref['semana_fim']),
                                                       size=13, width_field=145)
        self.field_start_saturday = createInputTextField("Começa (hh:mm)",
                                                         default_value=str(self.collaborator_ref['sabado_inicio']),
                                                         size=13, width_field=145)
        self.field_end_saturday = createInputTextField("Termina (hh:mm)",
                                                       default_value=str(self.collaborator_ref['sabado_fim']),
                                                       size=13, width_field=145)
        self.field_start_sunday = createInputTextField("Começa (hh:mm)",
                                                       default_value=str(self.collaborator_ref['domingo_inicio']),
                                                       size=13, width_field=145)
        self.field_end_sunday = createInputTextField("Termina (hh:mm)",
                                                     default_value=str(self.collaborator_ref['domingo_fim']),
                                                     size=13, width_field=145)

        self.type_collaborator = createDropdown("Escolha o nivel de acesso", set_value=self.user_ref['funcaoID'])

        for type in self.type_collaborator_ref:
            # Cada documento é um objeto com ID e dados     
            if type.id != "cliente":
                type_dropdown = self.type_collaborator.content
                _type_id = type.id
                _type_data = type.to_dict()
                _nome = type.id
                # adiciona no dropdown o atendente
                type_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _type_id,))

        self.text = createSubTitle("Informe o horário de atendimento", True)
        self.text2 = createSubTitle("Segunda a Sexta-feira:", True)
        self.text3 = createSubTitle("Sábado:", True)
        self.text4 = createSubTitle("Domingo:", True)

        self.checkbox_schedulling = createCheckbox("Permitir agendamento", set_visible=True, set_value=self.collaborator_ref['permitir_agendamento'])

        self.weekdays_button = createButtonWithVisibility("Dias de trabalho", visible=True, func=self.func3)

        self.row_day_week = ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=True,
                    controls=[
                        self.field_start_day_week,
                        self.field_end_day_week
                        ],
                )
        
        self.row_saturday = ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=True,
                    controls=[
                        self.field_start_saturday,
                        self.field_end_saturday,
                        ],
                )
        
        self.row_sunday = ft.Row(
                    alignment="center",
                    spacing=12,
                    visible=True,
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
                        self.field_name_text,
                        self.field_phone_text,
                    ],
                ),
                self.type_collaborator,
                self.checkbox_schedulling,
                self.text,
                self.text2,
                self.row_day_week,
                self.text3,
                self.row_saturday,
                self.text4,
                self.row_sunday,
                ft.Container(padding=5),
                self.weekdays_button,
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func2),
                
            ],
        )
    
async def view_edit_collaborator(page: ft.Page):

    stored_user = await loadStoredUser(page)
    stored_collaborator = await loadCollaboratorEdit(page)
    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    if stored_collaborator is None:
        page.go("/menu")
        view = ft.View()
        return view

    # Obtém referência ao Firestore
    db = get_firestore_client()
    type_collaboraty_ref = db.collection("funcoes").stream()
    id_collaborator = list(stored_collaborator.keys())[0]
    user_ref = db.collection("usuarios").document(id_collaborator).get()
    collaborator_ref = stored_collaborator[id_collaborator]

    # Função para abrir o diálogo de seleção dos dias da semana
    def open_weekday_dialog(e):
        dias_trabalhados = collaborator_ref.get('dias_trabalhados', [0, 1, 2, 3, 4, 5, 6])
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        
        checkboxes = []
        for i, dia in enumerate(dias_semana):
            checkboxes.append(
                ft.Checkbox(label=dia, value=(i in dias_trabalhados), data=i)
            )
        
        weekdays_dialog = ft.AlertDialog(
            title=ft.Text("Selecione os Dias da Semana"),
            scrollable=True,
            content=ft.Column(controls=checkboxes),
            actions=[ft.TextButton("OK", on_click=close_weekday_dialog)]
        )
        
        page.dialog = weekdays_dialog
        weekdays_dialog.open = True
        page.update()

    def close_weekday_dialog(e):
        checkboxes = page.dialog.content.controls
        work_days_selected = [cb.data for cb in checkboxes if cb.value]
        collaborator_ref['dias_trabalhados'] = work_days_selected
        
        page.dialog.open = False
        page.update()

    # Função assíncrona para atualizar o colaborador
    async def update_collaborator(e):
        nome, telefone, type_collaboraty, checkbox_scheduling, workday_start_time, workday_end_time, saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time = get_form_values()
        days_work = collaborator_ref.get('dias_trabalhados', [0, 1, 2, 3, 4, 5, 6])
        if check_fields():
            cadastro = register.UpdateCollaborator(
                nome, telefone, type_collaboraty, checkbox_scheduling, 
                workday_start_time, workday_end_time, 
                saturday_start_time, saturday_end_time, 
                sunday_start_time, sunday_end_time, 
                id_collaborator, days_work
            )
            cadastro.atualizar_colaborador()
            await removeCollaboratorEdit(page)
            texto = "Colaborador atualizado!"
            await transition.main(page, texto, None)  
        
    # Função para obter os valores do formulário
    def get_form_values():
        nome = _collaborator_.field_name_text.content.value
        telefone = _collaborator_.field_phone_text.content.value
        type_collaboraty = _collaborator_.type_collaborator.content.value
        checkbox_scheduling = _collaborator_.checkbox_schedulling.content.controls[0].value
        workday_start_time = _collaborator_.field_start_day_week.content.value
        workday_end_time = _collaborator_.field_end_day_week.content.value
        saturday_start_time = _collaborator_.field_start_saturday.content.value
        saturday_end_time = _collaborator_.field_end_saturday.content.value
        sunday_start_time = _collaborator_.field_start_sunday.content.value
        sunday_end_time = _collaborator_.field_end_sunday.content.value
        
        return nome, telefone, type_collaboraty, checkbox_scheduling, workday_start_time, workday_end_time, saturday_start_time, saturday_end_time, sunday_start_time, sunday_end_time
            
    # Função para verificar os campos do formulário
    def check_fields():
        
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

        nome = _collaborator_.field_name_text.content
        telefone = _collaborator_.field_phone_text.content
        type_collaboraty = _collaborator_.type_collaborator.content
        
        verifica = 0

        # Validação do campo de nome
        if nome.value == "":
            nome.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        else:
            nome.border_color = COLOR_BORDER_COLOR
        nome.update()


        # Validação do campo de telefone
        telefone_value = telefone.value.replace('-', "").replace("(", "").replace(")", "")
        if telefone.value == "" or len(telefone_value) < 10 or len(telefone_value) > 11:
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
        user_ref,
        collaborator_ref,
        update_collaborator,
        back_button,
        open_weekday_dialog,
    )

    return _collaborator_
