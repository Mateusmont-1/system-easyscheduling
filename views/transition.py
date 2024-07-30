import flet as ft
import asyncio

from utils.interface import createTextTransition, createMainColumn

class TransitionWidget(ft.Container):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                createTextTransition(self.text),
            ],
        )

async def main(page: ft.Page, texto: str = None, tela_inicial: bool = None):
    
    # Cria o conteúdo da transição
    _transicao_ = TransitionWidget(texto)
    _transicao_main = createMainColumn(page)
    _transicao_main.content.controls.append(ft.Container(padding=0))
    _transicao_main.content.controls.append(_transicao_)

    # Cria uma nova view para a transição
    view = ft.View(
        route='/transition',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[_transicao_main]
    )
    page.views.clear()
    # Adiciona a view e atualiza a página
    page.views.append(view)
    page.update()

    # Espera por 2.5 segundos
    await asyncio.sleep(2.5)

    # Limpa as views e redireciona conforme o parâmetro 'tela_inicial'
    if tela_inicial:
        page.go("/")
    else:
        page.go('/menu')
