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
        user,
        ):
        super().__init__()
        self.title = title
        self.func = func
        self.func2 = func2
        self.func3 = func3
        self.user = user

        # Criando as variaveis para aparecer ou não o botão na interface
        self._visible_create_service = False
        self._visible_edit_service = False
        # Botão de retornar é visivel para todos os tipos de usuario
        self._visible_back_ = True

        # De acordo com o perfil do usuario define a visibilidade dos botões que ele possui acesso 
        # como True
        if self.user['funcaoID'] == "colaborador":
            self._visible_create_scheduling = False
            self._visible_my_scheduling = False
            self._visible_check_scheduling = False
            
        elif self.user['funcaoID'] == "administrador":
            self._visible_create_service = True
            self._visible_edit_service = True
            # Botão de retornar é visivel para todos os tipos de usuario
            self._visible_back_ = True
            
        else:
            self._visible_create_scheduling = False
            self._visible_my_scheduling = False
            self._visible_check_scheduling = False

        self._create_service = createElevatedButton(text="Criar serviço", onClickFunc=self.func)
        self._edit_service = createElevatedButton(text="Editar servico", onClickFunc=self.func2)
        self._back_ = createElevatedButton(text="Voltar", onClickFunc=self.func3)
        
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
                            ft.Row(alignment="center",controls=[self._create_service]),
                            ft.Row(alignment="center", controls=[self._edit_service]),
                            ft.Row(alignment="center", controls=[self._back_]),
                        ]),
                    ft.Container(padding=5),
                ],
            )
    
async def view_menu_service(page: ft.Page):
    
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
    
    async def _create_servico(e):
        page.go('/cadastrar-servico')
        
    async def _check_servico(e):
        page.go('/verificar-servicos')
    
    async def _back_button(e):
        page.go('/menu')
    
    _menu_ = UserWidget(
        "Serviço!",
        _create_servico,
        _check_servico,
        _back_button,
        stored_user,
    )

    _menu_main = createMainColumn(page)
    _menu_main.content.controls.append(ft.Container(padding=0))
    _menu_main.content.controls.append(_menu_)

    return _menu_

    # view = ft.View(
    #     route='/menu-servico',
    #     horizontal_alignment="center",
    #     vertical_alignment="center",
    #     controls=[
    #         _menu_main,
    #     ]
    # )

    # return view
