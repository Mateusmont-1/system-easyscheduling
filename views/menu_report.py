import flet as ft

from utils.client_storage import loadStoredUser
from utils.interface import createMainColumn, createTitle, createButtonWithVisibility
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
        self._visible_check_barber = False
        self._visible_check_month = False
        self._visible_expenses = False
        # Botão de retornar é visivel para todos os tipos de usuario
        self._visible_back_ = True
        
        # De acordo com o perfil do usuario define a visibilidade dos botões que ele possui acesso 
        # como True
        if self.user['funcaoID'] == "colaborador":
            self._visible_check_barber = True
            
        elif self.user['funcaoID'] == "administrador":
            self._visible_check_barber = True
            self._visible_check_month = True
            self._visible_expenses = True
            
        else:
            ...

        self._check_barber = createButtonWithVisibility("Colaborador", func=self.func, visible=self._visible_check_barber)
        self._check_month = createButtonWithVisibility("Mensal", func=self.func2, visible=self._visible_check_month)
        self._expenses = createButtonWithVisibility("Despesas", func=self.func3, visible=self._visible_expenses)
        self._back_ = createButtonWithVisibility("Voltar", func=self.func4, visible=self._visible_back_)
        
        self.content = self.build()

    def build(self):
        if self.user['funcaoID'] == "administrador":
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(alignment="center",controls=[self._check_barber]),
                            ft.Row(alignment="center", controls=[self._check_month]),
                            ft.Row(alignment="center", controls=[self._expenses]),
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
                            ft.Row(alignment="center",controls=[self._check_barber]),
                            ft.Row(alignment="center", controls=[self._back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
        else:
            return ft.Column()
        
    
async def view_menu_report(page: ft.Page):
    
    stored_user = await loadStoredUser(page)

    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    
    elif stored_user['funcaoID'] == "cliente":
        page.go("/menu")
        view = ft.View()
        return view
    
    async def report_barber(e):
        page.go('/relatorio-colaborador')
        
    async def report_month(e):
        page.go('/relatorio-mensal')
    
    async def report_expense(e):
        page.go('/relatorio-despesa')
    
    async def back_button(e):
        page.go('/menu')

    _menu_ = UserWidget(
        "Relátorio!",
        report_barber,
        report_month,
        report_expense,
        back_button,
        stored_user,
    )

    return _menu_

    _menu_main = createMainColumn(page)
    _menu_main.content.controls.append(ft.Container(padding=0))
    _menu_main.content.controls.append(_menu_)

    view = ft.View(
        route='/menu-relatorio',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _menu_main,
        ]
    )

    return view
