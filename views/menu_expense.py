import flet as ft

from utils.client_storage import loadStoredUser
from utils.interface import createButtonWithVisibility, createMainColumn, createTitle, createElevatedButton
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

        self._create_category = createElevatedButton("Adicionar categoria", self.func)
        self._check_category = createElevatedButton("Verificar categorias", self.func2)
        self._check_expense = createElevatedButton("Verificar despesas", self.func3)
        self._back_ = createElevatedButton("Voltar", self.func4)
        
        self.content = self.build()

    def build(self):
        if self.user['funcaoID'] != "administrador":
            return ft.Column()
        
        else:
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(alignment="center",controls=[self._create_category]),
                            ft.Row(alignment="center", controls=[self._check_category]),
                            ft.Row(alignment="center", controls=[self._check_expense]),
                            ft.Row(alignment="center", controls=[self._back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
    
async def view_menu_expense(page: ft.Page):
    
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
    
    async def _create_category(e):
        page.go('/cadastrar-categoria')
        # tela_cadastro_servico.main(page, user)
        
    async def _check_category(e):
        pass

    async def _check_expense(e):
        pass

    async def _back_button(e):
        page.go("/menu")
    
    _menu_ = UserWidget(
        "Serviço!",
        _create_category,
        _check_category,
        _check_expense,
        _back_button,
        stored_user,
    )

    return _menu_

    _menu_main = createMainColumn(page)
    _menu_main.content.controls.append(ft.Container(padding=0))
    _menu_main.content.controls.append(_menu_)

    view = ft.View(
        route='/menu-produto',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _menu_main,
        ]
    )

    return view
