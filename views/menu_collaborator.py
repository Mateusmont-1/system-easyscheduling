import flet as ft

from utils.client_storage import loadStoredUser
from utils.interface import createMainColumn, createTitle, createElevatedButton
from utils.config import URL_MAPS

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        func,
        func2,
        func3,
        func4,
        user,
        ):
        super().__init__()
        self.title = title
        self.func = func
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        self.user = user

        self._create_collaborator = createElevatedButton(text="Criar colaborador", onClickFunc=self.func)
        self._edit_collaborator = createElevatedButton(text="Editar colaborador", onClickFunc=self.func2)
        self._day_off = createElevatedButton(text="Folga", onClickFunc=self.func3)
        self._back_ = createElevatedButton(text="Voltar", onClickFunc=self.func4)
        
        self.content = self.build()

    def build(self):
        if self.user['funcaoID'] != "administrador":
            return ft.Column()
        
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                ft.Container(padding=5),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Row(alignment="center",controls=[self._create_collaborator]),
                        ft.Row(alignment="center", controls=[self._edit_collaborator]),
                        ft.Row(alignment="center", controls=[self._day_off]),
                        ft.Row(alignment="center", controls=[self._back_]),
                    ]),
                ft.Container(padding=5),
            ],
        )
    
async def view_menu_collaborator(page: ft.Page):
    
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
    
    async def create_collaborator(e):
        page.go("/register_collaborator")

    async def check_collaborator(e):
        page.go('/verificar-colaborador')

    async def menu_day_off(e):
        print('create')
    
    async def back_button(e):
        page.go('/menu')

    _menu_ = UserWidget(
        "Menus!",
        create_collaborator,
        check_collaborator,
        menu_day_off,
        back_button,
        stored_user,
    )

    return _menu_

    _menu_main = createMainColumn(page)
    _menu_main.content.controls.append(ft.Container(padding=0))
    _menu_main.content.controls.append(_menu_)

    view = ft.View(
        route='/menu-colaborador',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _menu_main,
        ]
    )

    return view
