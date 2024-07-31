import flet as ft

from utils.interface import createButtonWithVisibility, createTitle

class UserWidget(ft.Container):
    def __init__(self, title):
        super().__init__()
        self.title = title

        self.content = self.build()

    def build(self):
        return ft.Column(
                controls=[createTitle(self.title)])
    
async def view_not_found(page: ft.Page):

    _not_found_ = UserWidget("Página não encontrada!")

    return _not_found_