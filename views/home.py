import flet as ft
from datetime import datetime

from utils.client_storage import (getEmail, getUser, setEmail, removeEmail, setUser)
from views import transition
from utils import login
from utils.validation import (
    validate_fields, is_valid_email, min_length_validator
)
from utils.encrypt import encryptUser
from utils.client_storage import loadStoredUser
from utils.interface import (
    createTitle, createSubTitle, createRememberCheckbox, createElevatedButton, 
    createButtonForgotPassword, createFooterText, createInputTextField, createMainColumn,
    createImageLogo
)
from utils.config import (
    COLOR_BORDER_COLOR_ERROR, IMG_LOGO
)

class UserWidget(ft.Container):
    def __init__(self, 
                 path_image:str,
                 title: str,
                 sub_title: str,
                 btn_name: str,
                 text: str,
                 stored_email,
                 on_sign_in_click,
                 on_forgot_password_click,
                 on_register_click):
        
        super().__init__()
        self.path_image = path_image
        self.title = title
        self._sub_title = sub_title
        self.btn_name = btn_name
        self.text = text
        self.stored_email = stored_email
        self.on_sign_in_click = on_sign_in_click
        self.on_forgot_password_click = on_forgot_password_click
        self.on_register_click = on_register_click

        self.field_email_text = createInputTextField("E-mail", False, self.stored_email, self.on_sign_in_click)
        self.field_password_text = createInputTextField("Senha", True, "", self.on_sign_in_click)
        self.field_remember_me = createRememberCheckbox(self.stored_email)
        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createImageLogo(self.path_image),
                createTitle(self.title),
                createSubTitle(self._sub_title),
                ft.Column(
                    spacing=12,
                    controls=[
                        self.field_email_text,
                        self.field_password_text,
                    ],
                ),
                self.field_remember_me,  # Passe o valor armazenado do email aqui
                ft.Container(padding=2),
                createElevatedButton(self.btn_name, self.on_sign_in_click),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                self.text,
                                size=15,
                                color="#C0C0C0",
                            )
                        ),
                        ft.TextButton(
                            content=ft.Text(
                                "cadastrar-se",
                                size=15,
                                color="#C0C0C0",
                            ),
                            on_click=self.on_register_click
                        )
                    ],
                ),
                createButtonForgotPassword(self.on_forgot_password_click),
                ft.Container(padding=1),
                createFooterText(),
            ],
        )

async def view_home(page: ft.Page):

    stored_user = await loadStoredUser(page)

    # Verifica se o usuario possui autenticação no navegador
    if stored_user != None:
        expiration_time = datetime.strptime(stored_user["expiration_time"], "%Y-%m-%d %H:%M:%S")

        # Caso sim redireciona para o menu
        if datetime.now() < expiration_time:
            page.go("/menu")
            view = ft.View()
            return view
        
    # Adicione uma função para carregar o email armazenado
    async def load_stored_email():
        stored_email = await getEmail(page)
        return stored_email

    async def sign_in_clicked(e):
        field_email = _sign_in_.field_email_text.content
        field_password = _sign_in_.field_password_text.content
        remember_me = _sign_in_.field_remember_me.content.controls[0].value

        if remember_me:
            # Armazenar o e-mail no armazenamento local
            await setEmail(page, field_email.value)
        else:
            # Remover o e-mail armazenado se o checkbox não estiver marcado
            await removeEmail(page)

        if checks_fields():
            conta = login.User(field_email.value, field_password.value)
            user = conta.login_firebase()
            if user == "email_not_found":
                field_email.border_color = COLOR_BORDER_COLOR_ERROR
                field_email.update()
            elif user == "incorrect_password":
                field_password.border_color = COLOR_BORDER_COLOR_ERROR
                field_password.update()
            elif user == "email_not_verified":
                texto = "E-mail de verificação enviado, verifique seu e-mail!"
                await transition.main(page, texto, True)
            elif user:
                encrypted_user = encryptUser(user)
                await setUser(page, encrypted_user)
                page.go('/menu')

    def checks_fields():
        return validate_fields([
            (_sign_in_.field_email_text, [is_valid_email]),
            (_sign_in_.field_password_text, [min_length_validator(6)])
        ])

    async def forgot_password_clicked(e):
        page.go('/forget-password')
        # Adicione sua lógica de recuperação de senha aqui

    async def register_clicked(e):
        page.go('/register')
        # Adicione sua lógica de registro aqui
    
    # Carregar o email armazenado e criar a instância de UserWidget
    stored_email = await load_stored_email()

    _sign_in_ = UserWidget(
        IMG_LOGO,
        "Bem vindo!",
        "Entre com os dados da sua conta abaixo",
        "Entrar",
        "Não tem uma conta?",
        stored_email,
        sign_in_clicked,
        forgot_password_clicked,
        register_clicked
    )

    return _sign_in_
    # _home_main = createMainColumn(page)
    # _home_main.content.controls.append(ft.Container(padding=0))
    # _home_main.content.controls.append(_sign_in_)

    # view = ft.View(
    #     route='/',
    #     horizontal_alignment="center",
    #     vertical_alignment="center",
    #     controls=[
    #         _home_main,
    #     ]
    # )

    # return view
