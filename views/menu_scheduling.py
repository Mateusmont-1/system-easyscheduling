import flet as ft

from utils.client_storage import loadStoredUser
from utils.interface import createButtonWithVisibility, createMainColumn, createTitle
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

        # Criando as variaveis para aparecer ou não o botão na interface
        self._visible_create_scheduling = False
        self._visible_my_scheduling = False
        self._visible_check_scheduling = False
        # Botão de retornar é visivel para todos os tipos de usuario
        self._visible_back_ = True
        
        # De acordo com o perfil do usuario define a visibilidade dos botões que ele possui acesso 
        # como True
        if self.user['funcaoID'] == "colaborador":
            self._visible_create_scheduling = True
            self._visible_my_scheduling = True
            self._visible_check_scheduling = True
            
        elif self.user['funcaoID'] == "administrador":
            self._visible_create_scheduling = True
            self._visible_my_scheduling = True
            self._visible_check_scheduling = True
            
        else:
            self._visible_create_scheduling = True
            self._visible_my_scheduling = True

        self._create_scheduling = createButtonWithVisibility("Criar agendamento", func=self.func, visible=self._visible_create_scheduling)
        self._my_scheduling = createButtonWithVisibility("Meus agendamentos", func=self.func2, visible=self._visible_my_scheduling)
        self._check_scheduling = createButtonWithVisibility("Verificar agendamentos", func=self.func3, visible=self._visible_check_scheduling)
        self._back_ = createButtonWithVisibility("Voltar", func=self.func4, visible=self._visible_back_)
        
        self.content = self.build()

    def build(self):
        if self.user['funcaoID'] == "cliente":
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(alignment="center",controls=[self._create_scheduling]),
                            ft.Row(alignment="center", controls=[self._my_scheduling]),
                            ft.Row(alignment="center", controls=[self._back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
        
        elif self.user['funcaoID'] == "colaborador":
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(alignment="center",controls=[self._create_scheduling]),
                            ft.Row(alignment="center", controls=[self._my_scheduling]),
                            ft.Row(alignment="center", controls=[self._check_scheduling]),
                            ft.Row(alignment="center", controls=[self._back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
        else:
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(alignment="center",controls=[self._create_scheduling]),
                            ft.Row(alignment="center", controls=[self._my_scheduling]),
                            ft.Row(alignment="center", controls=[self._check_scheduling]),
                            ft.Row(alignment="center", controls=[self._back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
    
async def view_menu_scheduling(page: ft.Page):
    
    stored_user = await loadStoredUser(page)

    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    
    async def create_scheduling(e):
        page.go('/criar-agendamento')

    async def my_scheduling(e):
        page.go('/verificar-meus-agendamento')

    async def check_scheduling(e):
        page.go('/verificar-agendamento')
    
    async def back_button(e):
        page.go('/menu')

    _menu_ = UserWidget(
        "Menus!",
        create_scheduling,
        my_scheduling,
        check_scheduling,
        back_button,
        stored_user,
    )

    return _menu_
    # _menu_main = createMainColumn(page)
    # _menu_main.content.controls.append(ft.Container(padding=0))
    # _menu_main.content.controls.append(_menu_)

    # view = ft.View(
    #     route='/menu-agendamento',
    #     horizontal_alignment="center",
    #     vertical_alignment="center",
    #     controls=[
    #         _menu_main,
    #     ]
    # )

    # return view
