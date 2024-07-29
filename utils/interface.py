import flet as ft
from functools import partial
import datetime

from utils.config import (
    COLOR_BORDER_COLOR_ERROR, COLOR_BACKGROUND_CONTAINER, COLOR_BORDER_COLOR, COLOR_TEXT,
    COLOR_TEXT_BUTTON, COLOR_TEXT_IN_BUTTON, COLOR_BACKGROUND_BUTTON, COLOR_TEXT_IN_FIELD,
    COLOR_BACKGROUND_TEXT_FIELD, COLOR_TEXT_IN_DROPDOWN
)

def createInputTextField(text: str, hide: bool=False, default_value: str = "", submit=None, width_field=275, type="email", size=16, set_read_only=False):
    text_field = ft.TextField(
        height=48,
        width=width_field,
        keyboard_type=type,
        read_only=set_read_only,
        value=default_value,
        bgcolor=COLOR_BACKGROUND_TEXT_FIELD,
        content_padding=10,
        text_size=size,
        color=COLOR_TEXT_IN_FIELD,
        border_color=COLOR_BORDER_COLOR,
        hint_text=text,
        filled=True,
        cursor_color=COLOR_TEXT,
        hint_style=ft.TextStyle(
            size=size,
            color=COLOR_TEXT_IN_FIELD,
        ),
        password=hide,
        can_reveal_password=hide,
    )
    
    if submit:
        text_field.on_submit = partial(submit)
    
    return ft.Container(
        alignment=ft.alignment.center,
        content=text_field,
    )

def createLogo(pathImage:str):
    return ft.Container(
        content=ft.Image(
            src=pathImage,
            width=150,  # Defina o tamanho desejado
            height=150,  # Defina o tamanho desejado
            fit=ft.ImageFit.COVER,
        ),
        width=150,
        height=150,
        border_radius=ft.border_radius.all(75),  # Torna a borda arredondada
    )

def createTitle(text:str, set_visible=True):
    return ft.Container(
        visible=set_visible,
        alignment=ft.alignment.center,
        content=ft.Text(
            text,
            size=30,
            text_align="center",
            weight="bold",
            color=COLOR_TEXT,
        ),
    )

def createSubTitle(text:str, set_visible:bool=True):
    return ft.Container(
        alignment=ft.alignment.center,
        visible=set_visible,
        content=ft.Text(
            text,
            text_align="center",
            color=COLOR_TEXT,
            size=25
        ),
    )

def createCheckbox(text, set_value:bool=False, set_visible:bool=True, set_func=None):
    checkbox = ft.Checkbox(label=text, value=set_value,label_style=ft.TextStyle(color=COLOR_TEXT_IN_FIELD),)

    if set_func:
        checkbox.on_change = partial(set_func)
    
    return ft.Container(
        alignment=ft.alignment.center,
        content=ft.Row(
            controls=[
            checkbox,
            ],
        visible=set_visible,
        alignment=ft.MainAxisAlignment.CENTER,
        ))

def createRememberCheckbox(storedEmail):
    return ft.Container(
        alignment=ft.alignment.center,
        content=ft.Row(
            controls=[
            ft.Checkbox(label="Lembrar-se", value=bool(storedEmail),label_style=ft.TextStyle(color=COLOR_TEXT_IN_FIELD),)
            ],
        alignment=ft.MainAxisAlignment.CENTER,
        ))

def createElevatedButton(text:str, onClickFunc):
    return ft.Container(
        content=ft.ElevatedButton(
            on_click=partial(onClickFunc),
            content=ft.Text(
                text,
                size=20,
                weight="bold",
            ),
            style=ft.ButtonStyle(
                shape={
                    "": ft.RoundedRectangleBorder(radius=8),
                },
                color={
                    "": "white",
                }
            ),
            color=COLOR_TEXT_IN_BUTTON,
            bgcolor=COLOR_BACKGROUND_BUTTON,
            height=48,
            width=275,
        )
    )

def createButtonForgotPassword(onClickFunc):
    return ft.TextButton(
        content=ft.Text(
            "Esqueceu a senha?",
            size=15,
            color=COLOR_TEXT_IN_FIELD,
        ),
        on_click=partial(onClickFunc),
    )

def createButtonWithVisibility(text, visible=False, func=None, url_text=None):
    container = ft.ElevatedButton(
                content=ft.Text(
                    text,
                    size=20,
                    weight="bold",
                ),
                style=ft.ButtonStyle(
                    shape={
                        "":ft.RoundedRectangleBorder(radius=8),
                    },
                    color={
                        "":"white",
                    }
                ),
                bgcolor=COLOR_BACKGROUND_BUTTON,
                color=COLOR_TEXT_IN_BUTTON,
                height=48,
                width=275,
            )
    
    if url_text:
        container.url = url_text

    if func:
        container.on_click = partial(func)

    return ft.Container(
            visible=visible,
            content=container)

def createFooterText():
    return ft.Container(
        alignment=ft.alignment.center,
        content=ft.Text(
            "Desenvolvido por Mateus Monteiro",
            size=12,
            weight=ft.FontWeight.W_400,
            color=COLOR_TEXT,
            text_align=ft.TextAlign.CENTER
        ),
    )

def createMainColumn(page):
    container = ft.Container(
        width=page_resize_initial(page, is_width=True),
        height=page_resize_initial(page, is_width=False),
        bgcolor=COLOR_BACKGROUND_CONTAINER,
        padding=12,
        border_radius=35,
        content=ft.Column(
            scroll="hidden",
            spacing=0,
            horizontal_alignment="center",
        )
    )
        
    page.on_resized = lambda e: page_resize_on_event(e, container=container, page=page)
    return container

def page_resize_initial(page: ft.Page, is_width: bool):
    if is_width:
        return 600 if page.width > 600 else page.width - 30
    else:
        return 600 if page.height > 600 else page.height - 60

def page_resize_on_event(e, container, page: ft.Page):
    largura = 600 if page.width > 600 else page.width - 30
    altura = 600 if page.height > 600 else page.height - 60
    container.width = largura
    container.height = altura
    page.update()

def createCheckboxTerms():
    return ft.Container(
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Checkbox(),
                            ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        "Ao aceitar você concorda com os ",
                                        ft.TextStyle(size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_IN_FIELD),
                                    ),
                                    ft.TextSpan(
                                        "Termos",
                                        ft.TextStyle(size=14, weight=ft.FontWeight.BOLD, color="blue", decoration=ft.TextDecoration.UNDERLINE),
                                        url="http://easyscheduling.com.br/termos-de-uso",
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        "de Uso",
                                        ft.TextStyle(size=14, weight=ft.FontWeight.BOLD, color="blue", decoration=ft.TextDecoration.UNDERLINE),
                                        url="http://easyscheduling.com.br/termos-de-uso",
                                    ),
                                    ft.TextSpan(
                                        " e a ",
                                        ft.TextStyle(size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_IN_FIELD),
                                    ),
                                    ft.TextSpan(
                                        "Política de Privacidade",
                                        ft.TextStyle(size=14, weight=ft.FontWeight.BOLD, color="blue", decoration=ft.TextDecoration.UNDERLINE),
                                        url="http://easyscheduling.com.br/politica-de-privacidade",
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                ],
                spacing=0,  # Ajuste o espaçamento entre os elementos
            ),
            visible=True,
        )

def createTextTransition(text):
        return ft.Container(
            alignment=ft.alignment.center,
            content=ft.Text(
                text,
                size=40,
                text_align="center",
                weight="bold",
                color=COLOR_TEXT,
            ),
        )


def createImageLogo(path_logo:str):
    return ft.Container(
                content=ft.Image(
                    src=path_logo,
                    width=150,  # Defina o tamanho desejado
                    height=150,  # Defina o tamanho desejado
                    fit=ft.ImageFit.COVER,
                ),
            width=150,
            height=150,
            border_radius=ft.border_radius.all(75),  # Torna a borda arredondada
            # clip_behavior=flet.ClipBehavior.ANTI_ALIAS,
        )

def createDropdown(text, func=None, set_visible=True, set_value=None):
    dropdown =  ft.Dropdown(label=text,
                                  label_style=ft.TextStyle(color=COLOR_TEXT_IN_DROPDOWN),
                                  width=275,
                                  border_color=COLOR_BORDER_COLOR,
                                  color=COLOR_TEXT_IN_DROPDOWN,
                                  bgcolor=COLOR_BACKGROUND_TEXT_FIELD,
                                  value=set_value,
                                  )
    
    if func:
        dropdown.on_change = partial(func)

    return ft.Container(
            visible=set_visible,
            alignment=ft.alignment.center,
            content=dropdown,
            )

def createDatePicker(func):
    return ft.Container(
            alignment=ft.alignment.center,
            content=ft.DatePicker(
                first_date=datetime.datetime.now(),
                last_date=datetime.datetime.now() + datetime.timedelta(days=15),
                on_change=partial(func),
            )
            )

def createCallDatePicker(text, ref_date_picker,set_visible=False,):
    return ft.Container(
            visible=set_visible,
            content=ft.ElevatedButton(
                on_click=lambda _: ref_date_picker.content.pick_date(),
                icon=ft.icons.CALENDAR_MONTH,
                text=text,
                style=ft.ButtonStyle(
                    shape={
                        "":ft.RoundedRectangleBorder
                        (radius=8),
                    },
                    color={
                        "":"white",
                    }
                ),
                bgcolor=COLOR_BACKGROUND_BUTTON,
                color=COLOR_TEXT_IN_BUTTON,
                height=48,
                width=275,
            )
        )

def createDataTable(visible=True, list_columns:list=[]):

    data_Table = ft.DataTable(columns=[])

    for name_columns in list_columns:
        data_Table.columns.append(
            ft.DataColumn(ft.Text(name_columns,
                                              text_align="center",
                                              weight="bold",
                                              color=COLOR_TEXT_IN_FIELD,))
        )

    return ft.Container(
            visible=visible,
            alignment=ft.alignment.center,
            content=ft.Row(
                scroll=True,
                controls=[data_Table]
            )
    )