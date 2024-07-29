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
        user,
        ):
        super().__init__()
        self.title = title
        self.func = func
        self.func2 = func2
        self.func3 = func3
        self.user = user

        # Criando as variaveis para aparecer ou não o botão na interface
        self._visible_create_day_off = False
        self._visible_check_day_off = False
        # Botão de retornar é visivel para todos os tipos de usuario
        self._visible_back_ = True
        
        # De acordo com o perfil do usuario define a visibilidade dos botões que ele possui acesso 
        # como True            
        if self.user['funcaoID'] == "administrador":
            self._visible_create_day_off = True
            self._visible_check_day_off = True
            self._visible_expenses = True
            
        else:
            ...

        self.create_day_off = createButtonWithVisibility("Cadastrar folga", func=self.func, visible=self._visible_create_day_off)
        self.check_day_off = createButtonWithVisibility("Verificar folga", func=self.func2, visible=self._visible_check_day_off)
        self.back_ = createButtonWithVisibility("Voltar", func=self.func3, visible=self._visible_back_)
        
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
                            ft.Row(alignment="center",controls=[self.create_day_off]),
                            ft.Row(alignment="center", controls=[self.check_day_off]),
                            ft.Row(alignment="center", controls=[self.back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
        
        else:
            return ft.Column()
        
    
async def view_menu_day_off(page: ft.Page):
    
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
    
    async def create_day_off(e):
        page.go("/cadastrar-folga")
        
    async def check_day_off(e):
        page.go("/verificar-folga")
    
    async def back_button(e):
        page.go('/menu')

    _menu_ = UserWidget(
        "Colaborador!",
        create_day_off,
        check_day_off,
        back_button,
        stored_user,
    )

    return _menu_

