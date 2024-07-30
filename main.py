import flet as ft
import datetime
import os

from utils.config import COLOR_BACKGROUND_PAGE
from utils.interface import createMainColumn, page_resize_on_event
from views.home import view_home
from views.register_client import view_register_client
from views.forget_password import view_forget_password
from views.menu import view_menu
from views.menu_scheduling import view_menu_scheduling
from views.menu_service import view_menu_service
from views.menu_product import view_menu_product
from views.menu_collaborator import view_menu_collaborator
from views.menu_report import view_menu_report
from views.menu_box import view_menu_box
from views.create_scheduling import view_create_scheduling
from views.check_my_scheduling import view_check_my_scheduling
from views.edit_scheduling import view_edit_scheduling
from views.create_service import view_create_service
from views.check_service import view_check_service
from views.edit_service import view_edit_service
from views.check_scheduling import view_check_scheduling
from views.finish_scheduling import view_finish_scheduling
from views.create_product import view_create_product
from views.check_product import view_check_product
from views.edit_product import view_edit_product
from views.register_collaborator import view_register_collaborator
from views.check_collaborator import view_check_collaborator
from views.edit_collaborator import view_edit_collaborator
from views.menu_day_off import view_menu_day_off
from views.create_day_off import view_create_day_off
from views.check_day_off import view_check_day_off
from views.check_report_collaborator import view_check_report_collaborator
from views.check_report_monthly import view_check_report_monthly
from views.check_report_monthly_expense import view_check_report_monthly_expense

# Dicionário de rotas
ROUTES = {
    "/": ("Login", view_home),
    "/register": ("Cadastro", view_register_client),
    "/forget-password": ("Esqueceu a senha", view_forget_password),
    "/menu": ("Menu", view_menu),
    "/menu-agendamento": ("Menu agendamento", view_menu_scheduling),
    "/menu-servico": ("Menu serviço", view_menu_service),
    "/menu-produto": ("Menu produto", view_menu_product),
    "/menu-colaborador": ("Menu colaborador", view_menu_collaborator),
    "/menu-relatorio": ("Menu relatorio", view_menu_report),
    "/menu-caixa": ("Menu caixa", view_menu_box),
    "/menu-folga": ("Menu folga", view_menu_day_off),
    "/criar-agendamento": ("Agendamento", view_create_scheduling),
    "/verificar-meus-agendamento": ("Agendamentos", view_check_my_scheduling),
    "/editar-agendamento": ("Editar agendamento", view_edit_scheduling),
    "/verificar-agendamento": ("Verificar agendamentos" , view_check_scheduling),
    "/finalizar-agendamento": ("Finalizar agendamento", view_finish_scheduling),
    "/cadastrar-servico": ("Cadastrar serviço", view_create_service),
    "/verificar-servicos": ("Verificar serviços", view_check_service),
    "/editar-servico": ("Editar serviço", view_edit_service),
    "/cadastrar-produto": ("Cadastrar produto", view_create_product),
    "/verificar-produtos": ("Verificar produtos", view_check_product),
    "/editar-produto": ("Editar produto", view_edit_product),
    "/registrar-colaborador": ("Cadastro colaborador", view_register_collaborator),
    "/verificar-colaborador": ("Verificar colaboradores", view_check_collaborator),
    "/editar-colaborador": ("Editar colaborador", view_edit_collaborator),
    "/cadastrar-folga": ("Cadastrar folga", view_create_day_off),
    "/verificar-folga": ("Verificar folga", view_check_day_off),
    "/relatorio-colaborador": ("Relátorio colaborador", view_check_report_collaborator),
    "/relatorio-mensal": ("Receita mensal", view_check_report_monthly),
    "/relatorio-despesa": ("Despesa mensal", view_check_report_monthly_expense)
}

async def main(page: ft.Page):
    page.bgcolor = COLOR_BACKGROUND_PAGE
    page.theme_mode = ft.ThemeMode.DARK
    page.theme_mode = "dark"

    main_column = createMainColumn(page)
    
    async def route_change(event: ft.RouteChangeEvent):
        page.views.clear()
        route = event.route  # Acessa a propriedade `route` do evento

        # Verifica se a rota está no dicionário
        if route in ROUTES:
            page.title, view_function = ROUTES[route]
            view_content = await view_function(page)
            
            if view_content is not None:
                main_column.content.controls.clear()
                main_column.content.controls.append(view_content)
                page.views.append(ft.View(
                    route=route,
                    horizontal_alignment="center",
                    vertical_alignment="center",
                    controls=[main_column]))
            else:
                page.views.append(ft.View(route=route, controls=[]))
        else:
            page.title = "Página não encontrada"
            # Aqui você pode adicionar uma função para uma página 404, se desejar
            # page.views.append(await view_not_found(page))

        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", port=8080, view=ft.WEB_BROWSER)