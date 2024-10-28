import flet as ft
import asyncio

from utils.client_storage import loadStoredUser
from utils.interface import createButtonWithVisibility, createTitle, createDashBoard, updateDashBoard
from utils.config import URL_MAPS, COLOR_BACKGROUND_BUTTON
from utils.client_storage import removeUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        func,
        func2,
        func3,
        func4,
        func5,
        func6,
        func7,
        user,
        ):
        super().__init__()
        self.title = title
        self.func = func
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        self.func5 = func5
        self.func6 = func6
        self.func7 = func7
        self.user = user

        self._visible_scheduling_ = False
        self._visible_service_ = False
        self._visible_product_ = False
        self._visible_collaborator_ = False
        self._visible_report_ = False
        self._visible_caixa_ = False
        self._visible_address_ = True
        self._visible_log_out_ = True
        
        if self.user['funcaoID'] == "colaborador":
            self._visible_scheduling_ = True
            self._visible_report_ = True
            self._visible_caixa_ = True
            self._dashboard = createDashBoard(self.user)
            
        elif self.user['funcaoID'] == "administrador":
            self._visible_scheduling_ = True
            self._visible_service_ = True
            self._visible_product_ = True
            self._visible_collaborator_ = True
            self._visible_report_ = True
            self._visible_caixa_ = True
            self._dashboard = createDashBoard(self.user)
        else:
            self._visible_scheduling_ = True

        self._scheduling_ = createButtonWithVisibility("Agendamento", func=self.func, visible=self._visible_scheduling_)
        self._service_ = createButtonWithVisibility("Serviço", func=self.func2, visible=self._visible_service_)
        self._product_ = createButtonWithVisibility("Produto", func=self.func3, visible=self._visible_product_)
        self._collaborator_ = createButtonWithVisibility("Colaborador", func=self.func4, visible=self._visible_collaborator_)
        self._report_ = createButtonWithVisibility("Relátorio", func=self.func5, visible=self._visible_report_)
        self._caixa_ = createButtonWithVisibility("Caixa", func=self.func6, visible=self._visible_caixa_)
        self._address_ = createButtonWithVisibility("Endereço", visible=self._visible_address_, url_text=URL_MAPS)
        self._log_out_ = createButtonWithVisibility("Deslogar", func=self.func7, visible=self._visible_log_out_)

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
                            ft.Row(alignment="center",controls=[self._scheduling_]),
                            ft.Row(alignment="center", controls=[self._address_]),
                            ft.Row(alignment="center", controls=[self._log_out_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
        
        elif self.user['funcaoID'] == "colaborador":
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    self._dashboard,
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Row(alignment="center",controls=[self._scheduling_]),
                            ft.Row(alignment="center", controls=[self._report_]),
                            ft.Row(alignment="center", controls=[self._caixa_]),
                            ft.Row(alignment="center", controls=[self._address_]),
                            ft.Row(alignment="center", controls=[self._log_out_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
        else:
            return ft.Column(
                horizontal_alignment="center",
                controls=[
                    createTitle(self.title),
                    self._dashboard,
                    ft.Container(padding=5),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                        ft.Row(alignment="center",controls=[self._scheduling_]),
                        ft.Row(alignment="center",controls=[self._service_]),
                        ft.Row(alignment="center",controls=[self._product_]),
                        ft.Row(alignment="center", controls=[self._collaborator_]),
                        ft.Row(alignment="center", controls=[self._report_]),
                        ft.Row(alignment="center", controls=[self._caixa_]),
                        ft.Row(alignment="center", controls=[self._address_]),
                        ft.Row(alignment="center", controls=[self._log_out_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
    
async def view_menu(page: ft.Page):
    
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return None
    
    async def _button_scheduling(e):
        page.go('/menu-agendamento')

    async def _button_service(e):
        page.go('/menu-servico')

    async def _button_product(e):
        page.go('/menu-produto')

    async def _button_collaborator(e):
        page.go('/menu-colaborador')

    async def _button_report(e):
        page.go('/menu-relatorio')

    async def _button_caixa(e):
        page.go('/menu-caixa')

    async def _button_log_out(e):
        await removeUser(page)
        page.go("/")

    _menu_ = UserWidget(
        "Tela inicial!",
        _button_scheduling,
        _button_service,
        _button_product,
        _button_collaborator,
        _button_report,
        _button_caixa,
        _button_log_out,
        stored_user,
    )

    # # Renderiza o dashboard com loading inicial
    # if _menu_._dashboard:
    #     await updateDashBoard(_menu_._dashboard, _menu_.user)  # Atualiza o dashboard com os dados reais

    return _menu_
