# import flet as ft
# import asyncio
# from functools import partial

# from utils.client_storage import loadStoredUser
# from utils.interface import createButtonWithVisibility, createTitle, createDashBoard, updateDashBoard
# from utils.config import URL_MAPS, COLOR_BACKGROUND_BUTTON
# from utils.client_storage import removeUser

# class UserWidget(ft.Container):
#     def __init__(
#         self,
#         title:str,
#         func,
#         func2,
#         func3,
#         func4,
#         func5,
#         func6,
#         func7,
#         user,
#         ):
#         super().__init__()
#         self.title = title
#         self.func = func
#         self.func2 = func2
#         self.func3 = func3
#         self.func4 = func4
#         self.func5 = func5
#         self.func6 = func6
#         self.func7 = func7
#         self.user = user

#         self._visible_scheduling_ = False
#         self._visible_service_ = False
#         self._visible_product_ = False
#         self._visible_collaborator_ = False
#         self._visible_report_ = False
#         self._visible_caixa_ = False
#         self._visible_address_ = True
#         self._visible_log_out_ = True
        
#         if self.user['funcaoID'] == "colaborador":
#             self._visible_scheduling_ = True
#             self._visible_report_ = True
#             self._visible_caixa_ = True
#             self._dashboard = createDashBoard(self.user)
            
#         elif self.user['funcaoID'] == "administrador":
#             self._visible_scheduling_ = True
#             self._visible_service_ = True
#             self._visible_product_ = True
#             self._visible_collaborator_ = True
#             self._visible_report_ = True
#             self._visible_caixa_ = True
#             self._dashboard = createDashBoard(self.user)
#         else:
#             self._visible_scheduling_ = True

#         self.bottom_sheet = ft.BottomSheet(
#             ft.Container(
#                 content=ft.Column(
#                     controls=[
#                         ft.Text("This is a BottomSheet"),
#                         ft.ElevatedButton("Close", on_click=partial(self.func2)),  # Use close function here
#                     ],
#                     tight=False,
#                 ),
#                 padding=10,
#                 bgcolor=ft.colors.WHITE,
#             ),
#             open=False,  # Initially closed
#         )
#         self._scheduling_ = createButtonWithVisibility("Teste", func=self.func, visible=self._visible_scheduling_)
#         self._service_ = createButtonWithVisibility("Serviço", func=self.func2, visible=self._visible_service_)
#         self._product_ = createButtonWithVisibility("Produto", func=self.func3, visible=self._visible_product_)
#         self._collaborator_ = createButtonWithVisibility("Colaborador", func=self.func4, visible=self._visible_collaborator_)
#         self._report_ = createButtonWithVisibility("Relátorio", func=self.func5, visible=self._visible_report_)
#         self._caixa_ = createButtonWithVisibility("Caixa", func=self.func6, visible=self._visible_caixa_)
#         self._address_ = createButtonWithVisibility("Endereço", visible=self._visible_address_, url_text=URL_MAPS)
#         self._log_out_ = createButtonWithVisibility("Deslogar", func=self.func7, visible=self._visible_log_out_)

#         self.content = self.build()

#     def build(self):
        
#         return ft.Column(
#             horizontal_alignment="center",
#             controls=[
#                 createTitle(self.title),
#                 self._dashboard,
#                 ft.Container(padding=5),
#                 ft.Column(
#                     alignment=ft.MainAxisAlignment.CENTER,
#                     controls=[
#                     ft.Row(alignment="center",controls=[self._scheduling_]),
#                     # ft.Row(alignment="center",controls=[self._service_]),
#                     # ft.Row(alignment="center",controls=[self._product_]),
#                     # ft.Row(alignment="center", controls=[self._collaborator_]),
#                     # ft.Row(alignment="center", controls=[self._report_]),
#                     # ft.Row(alignment="center", controls=[self._caixa_]),
#                     # ft.Row(alignment="center", controls=[self._address_]),
#                     # ft.Row(alignment="center", controls=[self._log_out_]),
#                     ]),
#                 ft.Container(padding=5),
#                 self.bottom_sheet,
#             ],
#         )
    
# async def view_teste(page: ft.Page):
    
#     stored_user = await loadStoredUser(page)

#     if stored_user is None:
#         page.go("/")
#         return None
    
#     # Function to open BottomSheet
#     def open_bottom_sheet(event):
#         _menu_.bottom_sheet.open = True
#         # page.overlay.append(_menu_.bottom_sheet)
#         print(_menu_.bottom_sheet.open)
#         page.update()  # Update the page to reflect changes

#     # Function to close BottomSheet
#     def close_bottom_sheet(event):
#         _menu_.bottom_sheet.open = False
#         print(_menu_.bottom_sheet.open)
#         page.update()  # Update the page to reflect changes


#     async def _button_scheduling(e):
#         page.go('/menu-agendamento')

#     async def _button_service(e):
#         page.go('/menu-servico')

#     async def _button_product(e):
#         page.go('/menu-produto')

#     async def _button_collaborator(e):
#         page.go('/menu-colaborador')

#     async def _button_report(e):
#         page.go('/menu-relatorio')

#     async def _button_caixa(e):
#         page.go('/menu-caixa')

#     async def _button_log_out(e):
#         await removeUser(page)
#         page.go("/")

#     _menu_ = UserWidget(
#         "Tela inicial!",
#         open_bottom_sheet,
#         close_bottom_sheet,
#         _button_product,
#         _button_collaborator,
#         _button_report,
#         _button_caixa,
#         _button_log_out,
#         stored_user,
#     )

#     # # Renderiza o dashboard com loading inicial
#     # if _menu_._dashboard:
#     #     await updateDashBoard(_menu_._dashboard, _menu_.user)  # Atualiza o dashboard com os dados reais

#     return _menu_

# import flet as ft
# import asyncio
# from functools import partial

# from utils.client_storage import loadStoredUser
# from utils.interface import createButtonWithVisibility, createTitle, createDashBoard, updateDashBoard
# from utils.config import URL_MAPS, COLOR_BACKGROUND_BUTTON
# from utils.client_storage import removeUser

# class UserWidget(ft.Container):
#     def __init__(
#         self,
#         title: str,
#         func,
#         func2,
#         func3,
#         func4,
#         func5,
#         func6,
#         func7,
#         user,
#     ):
#         super().__init__()
#         self.title = title
#         self.func = func
#         self.func2 = func2
#         self.func3 = func3
#         self.func4 = func4
#         self.func5 = func5
#         self.func6 = func6
#         self.func7 = func7
#         self.user = user

#         self._visible_scheduling_ = False
#         self._visible_service_ = False
#         self._visible_product_ = False
#         self._visible_collaborator_ = False
#         self._visible_report_ = False
#         self._visible_caixa_ = False
#         self._visible_address_ = True
#         self._visible_log_out_ = True

#         if self.user['funcaoID'] == "colaborador":
#             self._visible_scheduling_ = True
#             self._visible_report_ = True
#             self._visible_caixa_ = True
#             self._dashboard = createDashBoard(self.user)

#         elif self.user['funcaoID'] == "administrador":
#             self._visible_scheduling_ = True
#             self._visible_service_ = True
#             self._visible_product_ = True
#             self._visible_collaborator_ = True
#             self._visible_report_ = True
#             self._visible_caixa_ = True
#             self._dashboard = createDashBoard(self.user)
#         else:
#             self._visible_scheduling_ = True

#         self.bottom_container = ft.Container(
#             content=ft.Column(
#                 controls=[
#                     ft.Text("This is a custom BottomSheet-like Container"),
#                     ft.ElevatedButton("Close", on_click=partial(self.func2)),
#                 ],
#                 tight=False,
#             ),
#             padding=10,
#             bgcolor=ft.colors.WHITE,
#             margin=ft.margin.only(bottom=300),  # Inicialmente posicionado fora da tela (oculto)
#             animate=ft.Animation(600, ft.AnimationCurve.LINEAR),  # Animação aplicada ao container
#             opacity=0,  # Inicialmente invisível
#             animate_opacity=ft.Animation(300),  # Animação de opacidade
#         )

#         self._scheduling_ = createButtonWithVisibility("Teste", func=self.func, visible=self._visible_scheduling_)
#         self._service_ = createButtonWithVisibility("Serviço", func=self.func2, visible=self._visible_service_)
#         self._product_ = createButtonWithVisibility("Produto", func=self.func3, visible=self._visible_product_)
#         self._collaborator_ = createButtonWithVisibility("Colaborador", func=self.func4, visible=self._visible_collaborator_)
#         self._report_ = createButtonWithVisibility("Relátorio", func=self.func5, visible=self._visible_report_)
#         self._caixa_ = createButtonWithVisibility("Caixa", func=self.func6, visible=self._visible_caixa_)
#         self._address_ = createButtonWithVisibility("Endereço", visible=self._visible_address_, url_text=URL_MAPS)
#         self._log_out_ = createButtonWithVisibility("Deslogar", func=self.func7, visible=self._visible_log_out_)

#         self.content = self.build()

#     def build(self):
#         return ft.Column(
#             horizontal_alignment="center",
#             controls=[
#                 createTitle(self.title),
#                 self._dashboard,
#                 ft.Container(padding=5),
#                 ft.Column(
#                     alignment=ft.MainAxisAlignment.CENTER,
#                     controls=[
#                         ft.Row(alignment="center", controls=[self._scheduling_]),
#                     ],
#                 ),
#                 ft.Container(padding=5),
#                 self.bottom_container,
#             ],
#         )

# async def view_teste(page: ft.Page):

#     stored_user = await loadStoredUser(page)

#     if stored_user is None:
#         page.go("/")
#         return None

#     # Function to open custom BottomSheet
#     def open_bottom_container(event):
#         _menu_.bottom_container.margin = ft.margin.only(bottom=0)  # Move it into the screen
#         _menu_.bottom_container.opacity = 1  # Torna visível
#         page.update()

#     # Function to close custom BottomSheet
#     def close_bottom_container(event):
#         _menu_.bottom_container.margin = ft.margin.only(bottom=300)  # Move it out of the screen
#         _menu_.bottom_container.opacity = 0  # Torna invisível
#         page.update()

#     async def _button_scheduling(e):
#         page.go('/menu-agendamento')

#     async def _button_service(e):
#         page.go('/menu-servico')

#     async def _button_product(e):
#         page.go('/menu-produto')

#     async def _button_collaborator(e):
#         page.go('/menu-colaborador')

#     async def _button_report(e):
#         page.go('/menu-relatorio')

#     async def _button_caixa(e):
#         page.go('/menu-caixa')

#     async def _button_log_out(e):
#         await removeUser(page)
#         page.go("/")

#     _menu_ = UserWidget(
#         "Tela inicial!",
#         open_bottom_container,
#         close_bottom_container,
#         _button_product,
#         _button_collaborator,
#         _button_report,
#         _button_caixa,
#         _button_log_out,
#         stored_user,
#     )

#     return _menu_

import flet as ft
import asyncio
from functools import partial

from utils.client_storage import loadStoredUser
from utils.interface import createButtonWithVisibility, createTitle, createDashBoard, createMainColumn
from utils.config import URL_MAPS
from utils.client_storage import removeUser

class UserWidget(ft.Container):
    def __init__(
        self,
        title: str,
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

        self.bottom_container = ft.Container(
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            width=600,
            height=600,
            bgcolor=ft.colors.WHITE,
            padding=12,
            border_radius=35,
            content=ft.Column(
                scroll="hidden",
                spacing=0,
                horizontal_alignment="center",
            )
        )
        # ft. Container(
        #     content=ft. Column(
        #     controls=[
        #         ft. Text("This is a custom BottomSheet-like Container"),
        #         ft. ElevatedButton("Close", on_click=partial(self.func2)),
        #         ],
        #         tight=False,
        #         scroll="hidden",
        #         spacing=0,
        #         horizontal_alignment="center",
        #     ),
        #     alignment=ft.alignment.center, # Centraliza o container na tela
        #     padding=12,
        #     border_radius=35,
        #     bgcolor=ft.colors.WHITE,
        #     opacity=0, # Inicialmente oculto
        #     animate_opacity=ft. Animation(300),
        #     animate=ft. Animation(600, ft. AnimationCurve.LINEAR),
        #     width=300,
        #     height=200, # Defina a altura desejada
        # )

        self._scheduling_ = createButtonWithVisibility("Teste", func=self.func, visible=self._visible_scheduling_)
        self._service_ = createButtonWithVisibility("Serviço", func=self.func2, visible=self._visible_service_)
        self._product_ = createButtonWithVisibility("Produto", func=self.func3, visible=self._visible_product_)
        self._collaborator_ = createButtonWithVisibility("Colaborador", func=self.func4, visible=self._visible_collaborator_)
        self._report_ = createButtonWithVisibility("Relátorio", func=self.func5, visible=self._visible_report_)
        self._caixa_ = createButtonWithVisibility("Caixa", func=self.func6, visible=self._visible_caixa_)
        self._address_ = createButtonWithVisibility("Endereço", visible=self._visible_address_, url_text=URL_MAPS)
        self._log_out_ = createButtonWithVisibility("Deslogar", func=self.func7, visible=self._visible_log_out_)

        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self._dashboard,
                ft.Container(padding=5),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Row(alignment="center", controls=[self._scheduling_]),
                    ],
                ),
                ft.Container(padding=5),
            ],
        )

async def view_teste(page: ft.Page):

    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return None

    def open_bottom_container(event):
        # _menu_.bottom_container.margin = ft.margin.only(bottom=0)
        _menu_.bottom_container.opacity = 1
        page.update()

    def close_bottom_container(event):
        # _menu_.bottom_container.margin = ft.margin.only(bottom=-300)
        _menu_.bottom_container.opacity = 0
        page.update()

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
        open_bottom_container,
        close_bottom_container,
        _button_product,
        _button_collaborator,
        _button_report,
        _button_caixa,
        _button_log_out,
        stored_user,
    )

    # Add bottom_container to the page overlay
    page.overlay.append(_menu_.bottom_container)

    return _menu_