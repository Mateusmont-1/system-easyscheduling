import flet as ft
from email_validator import validate_email, EmailNotValidError

from utils.interface import (
    createTitle, createSubTitle, createRememberCheckbox, createElevatedButton, 
    createButtonForgotPassword, createFooterText, createInputTextField, createMainColumn,
    createCheckboxTerms
)
from utils.validation import (
    validate_fields, is_valid_email, length_validator, ddd_validator, phone_validator, checkbox_validator, min_length_validator,
)
from utils.config import (COLOR_BORDER_COLOR_ERROR,COLOR_BORDER_COLOR)
from utils.client_storage import setEmail
from utils import register
from utils import login
from views import transition

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        func,
        func2,
        ):
        super().__init__()
        self.title = title
        self._sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.func = func
        self.func2 = func2
        
        self.field_email_text = createInputTextField("E-mail", False)
        self.field_password_text = createInputTextField("Senha", True)
        self.field_name_text = createInputTextField("Nome", False)
        self.field_ddd_text = createInputTextField("DDD (Ex:11)", width_field=97.5, size=12, type="phone")
        self.field_number_text = createInputTextField("Telefone", width_field=167.5, size=12, type="phone")
        self.checkbox_terms = createCheckboxTerms()
        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                createSubTitle(self._sub_title),
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
                        self.field_number_text,
                        ],
                ),
                self.checkbox_terms,
                ft.Container(padding=5),
                createElevatedButton(self.btn_name, self.func),
                createElevatedButton(self.btn_name2, self.func2),
            ]
        )


async def view_register_client(page: ft.Page):

    # Função assíncrona para voltar à página de login
    async def _back_button(e):
        print("back")
        page.go("/")

    async def _register_client(e):
        # Função para verificar os campos do formulário
        if checks_fields():
            email = _register_client_.field_email_text.content.value
            password = _register_client_.field_password_text.content.value
            name = _register_client_.field_name_text.content.value
            ddd = _register_client_.field_ddd_text.content.value
            number = _register_client_.field_number_text.content.value
            checkbox_termos = _register_client_.checkbox_terms.content.controls[0].controls[0].value
            number_complet = f'({ddd}){number.replace("-", "")}'
            cadastro = register.User(email, password, name, number_complet, checkbox_termos)
            cadastro.create_account()

            # Save email to cache do navegador
            await setEmail(page, email)

            if cadastro.uid:
                conta = login.User(email, password)
                acesso = conta.login_firebase()

                if acesso == "email_not_verified":
                    texto = "E-mail de verificação enviado, verifique seu e-mail!"
                    await transition.main(page, texto, True)
                elif acesso:
                    print("dasd")
                    # await tela_menu_main.main(page, acesso)
            else:
                email = _register_client_.field_email_text.content
                email.border_color = COLOR_BORDER_COLOR_ERROR
                email.value = "E-mail informado em uso"
                email.update()

    def checks_fields():
        return validate_fields([
            (_register_client_.field_email_text, [is_valid_email]),
            (_register_client_.field_password_text, [min_length_validator(6)]),
            (_register_client_.field_name_text, [min_length_validator(1)]),
            (_register_client_.field_ddd_text, [ddd_validator]),
            (_register_client_.field_number_text, [phone_validator]),
            (_register_client_.checkbox_terms.content.controls[0].controls[0], [checkbox_validator])
        ])

    # Criação do widget de registro de usuário
    _register_client_ = UserWidget(
        "Registrar-se!",
        "Entre com os dados da sua conta abaixo",
        "Registrar",
        "Voltar",
        _register_client,
        _back_button,
    )

    return _register_client_

    # Configuração do contêiner principal e adição do widget de registro
    _register_client_main = createMainColumn(page)
    _register_client_main.content.controls.append(ft.Container(padding=0))
    _register_client_main.content.controls.append(_register_client_)

    view = ft.View(
        route='/register',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _register_client_main,
        ]
    )

    return view