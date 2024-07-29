import flet as ft

from views import transition
from utils import login
from utils.validation import (validate_fields, is_valid_email)

from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO


class UserWidget(ft.Container):
    def __init__(self,
        image,
        title:str,
        sub_title:str,
        btn_name:str,
        btn_name2:str,
        func1,
        func2,
        ):
        super().__init__()
        self.image = image
        self.title = title
        self.sub_title = sub_title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.func = func1
        self.func2 = func2

        self.field_email_text = createInputTextField("E-mail", False, "", self.func)
        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createImageLogo(self.image),
                createTitle(self.title),
                createSubTitle(self.sub_title),
                ft.Column(
                    spacing=12,
                    controls=[
                        self.field_email_text,
                    ],
                ),
                ft.Container(padding=5),
                createElevatedButton(text=self.btn_name, onClickFunc=self.func),
                createElevatedButton(text=self.btn_name2, onClickFunc=self.func2),
                ft.Container(padding=35),
                createFooterText(),
            ],
        )


async def view_forget_password(page:ft.page):

    async def reset_password(e):
        if checks_fields():
            email = _forget_.field_email_text.content
            conta = login.ForgetPassword(email.value)
            redefinir = conta.redefine_password()
            if redefinir:
                texto = "E-mail para redefinir senha enviado"
                await transition.main(page, None, texto, True)
            else:
                email.border_color = COLOR_BORDER_COLOR_ERROR
                email.update()
                # Muda a cor do campo de e-mail indicando erro

    def checks_fields():
        return validate_fields([
            (_forget_.field_email_text, [is_valid_email]),
        ])
    
    async def back_button(e):
        page.go("/")

    _forget_ = UserWidget(
        IMG_LOGO,
        "Redefinir senha",
        "Entre com os dados da sua conta abaixo",
        "Redefinir",
        "Voltar",
        reset_password,
        back_button,
    )

    return _forget_

    _forget_main = createMainColumn(page)
    _forget_main.content.controls.append(ft.Container(padding=0))
    _forget_main.content.controls.append(_forget_)

    view = ft.View(
        route='/forget-password',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _forget_main,
        ]
    )

    return view
    