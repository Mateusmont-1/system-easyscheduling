import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import login
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
    createButtonWithVisibility
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO
from utils.client_storage import loadStoredUser, loadSchedulingFinish
from utils import whatsapp
from utils.whatsapp import TELEFONE_CONTACT
from utils import scheduling_db
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
# from utils.scheduling_utils import processa_colaborador

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        product_ref,
        service_ref,
        collaborator_ref,
        func1,
        func2,
        func3,
        func4,
        ):
        super().__init__()
        self.title = title
        self.product_ref = product_ref
        self.service_ref = service_ref
        self.collaborator_ref = collaborator_ref
        self.func = func1
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        
        self.collaborator_id = ""
        self.service = dict()
        self.service_dict = {}
        self.product_dict = {}
        self.price_products = 0.0

        self.date_picker = createDatePickerForScheduling(self.func4, set_days=1, set_days_before=31)
        self.day_choose = createCallDatePicker("Escolha o dia", self.date_picker, True)

        self.service_choose = createDropdown("Escolha o Serviço", self.func2, set_visible=False)
        self.service_choose2 = createDropdown("Escolha o Serviço", self.func2, set_visible=False)
        self.service_choose3 = createDropdown("Escolha o Serviço", self.func2, set_visible=False)
        self.service_choose4 = createDropdown("Escolha o Serviço", self.func2, set_visible=False)
        self.service_choose5 = createDropdown("Escolha o Serviço", self.func2, set_visible=False)

        # Adicionando no dropdown a opção de nenhum serviço
        self.service_choose.content.options.append(ft.dropdown.Option(text= "Nenhum serviço", key= "Nenhum", ))
        self.service_choose2.content.options.append(ft.dropdown.Option(text= "Nenhum serviço", key= "Nenhum", ))
        self.service_choose3.content.options.append(ft.dropdown.Option(text= "Nenhum serviço", key= "Nenhum", ))
        self.service_choose4.content.options.append(ft.dropdown.Option(text= "Nenhum serviço", key= "Nenhum", ))
        self.service_choose5.content.options.append(ft.dropdown.Option(text= "Nenhum serviço", key= "Nenhum", ))

        self.service_dict["Nenhum"] = {'nome': 'Nenhum', 'preco': 0.0}

        for _service in self.service_ref:
            # Cada documento é um objeto com ID e dados
            service = self.service_choose.content
            service2 = self.service_choose2.content
            service3 = self.service_choose3.content
            service4 = self.service_choose4.content
            service5 = self.service_choose5.content
            _service_id = _service.id
            _service_data = _service.to_dict()
            
            if _service_data['permitir_agendamento']:
                _nome = f'{_service_data["nome"]} R${_service_data["preco"]}'
                #adiciona no dropdown o Servico
                service.options.append(ft.dropdown.Option(text= _nome, key= _service_id, ))
                service2.options.append(ft.dropdown.Option(text= _nome, key= _service_id, ))
                service3.options.append(ft.dropdown.Option(text= _nome, key= _service_id, ))
                service4.options.append(ft.dropdown.Option(text= _nome, key= _service_id, ))
                service5.options.append(ft.dropdown.Option(text= _nome, key= _service_id, ))

                self.service_dict[_service_id] = _service_data

        self.collaborator_choose = createDropdown("Escolha o(a) atendente", set_visible=False)

        for _collaborator in self.collaborator_ref:
            collaborator = self.collaborator_choose.content
            _collaborator_id = _collaborator.id
            _collaborator_date = _collaborator.to_dict()
            if _collaborator_date['permitir_agendamento']:
                _nome = f'{_collaborator_date["nome"]}'
                collaborator.options.append(ft.dropdown.Option(text= _nome, key=_collaborator_id))
        
        self.product_choose = createDropdown("Escolha outro produto", self.func2, False)
        self.product_choose2 = createDropdown("Escolha outro produto", self.func2, False)
        self.product_choose3 = createDropdown("Escolha outro produto", self.func2, False)
        self.product_choose4 = createDropdown("Escolha outro produto", self.func2, False)
        self.product_choose5 = createDropdown("Escolha outro produto", self.func2, False)

        # Adicionando opção para remover produto
        self.product_choose.content.options.append(ft.dropdown.Option(text= "Nenhum produto", key= "Nenhum", ))
        self.product_choose2.content.options.append(ft.dropdown.Option(text= "Nenhum produto", key= "Nenhum", ))
        self.product_choose3.content.options.append(ft.dropdown.Option(text= "Nenhum produto", key= "Nenhum", ))
        self.product_choose4.content.options.append(ft.dropdown.Option(text= "Nenhum produto", key= "Nenhum", ))
        self.product_choose5.content.options.append(ft.dropdown.Option(text= "Nenhum produto", key= "Nenhum", ))
        
        self.product_dict["Nenhum"] = {'nome': 'Nenhum', 'preco': 0.0}
        
        # Preenchendo os Dropdown de produto
        for _product in self.product_ref:
            product = self.product_choose.content
            product2 = self.product_choose2.content
            product3 = self.product_choose3.content
            product4 = self.product_choose4.content
            product5 = self.product_choose5.content
            
            _product_id = _product.id
            _product_date = _product.to_dict()
            
            if _product_date['permitir_venda']:
                _nome = f'{_product_date["nome"]} R${_product_date["preco"]}'
                product.options.append(ft.dropdown.Option(text= _nome, key=_product_id))
                product2.options.append(ft.dropdown.Option(text= _nome, key=_product_id))
                product3.options.append(ft.dropdown.Option(text= _nome, key=_product_id))
                product4.options.append(ft.dropdown.Option(text= _nome, key=_product_id))
                product5.options.append(ft.dropdown.Option(text= _nome, key=_product_id))
            
                self.product_dict[_product_id] = _product_date
            
        self.price = createInputTextField("Preço total",set_visible=False)

        self.button_finish = createButtonWithVisibility("Cadastrar atendimento",visible=False, func=self.func)

        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self.day_choose,
                self.collaborator_choose,
                self.service_choose,
                self.service_choose2,
                self.service_choose3,
                self.service_choose4,
                self.service_choose5,
                self.product_choose,
                self.product_choose2,
                self.product_choose3,
                self.product_choose4,
                self.product_choose5,
                createSubTitle("Preço total",set_visible=False),
                ft.Column(
                    spacing=0,
                    controls=[
                        self.price,
                    ],
                ),
                ft.Container(padding=3),
                self.button_finish,
                createElevatedButton("Voltar", self.func3),
                self.date_picker,
            ],
        )
    
async def view_register_finish_scheduling(page: ft.Page):

    stored_user = await loadStoredUser(page)
    # Se não possuir user armazenado retorna para tela home
    if stored_user is None or stored_user['funcaoID'] == "cliente":
        page.go("/")
        view = ft.View()
        return view
    
    db = get_firestore_client()
    service_ref = db.collection("servico").stream()
    
    data_formatada = None

    product_ref = db.collection("produto").stream()
    collaborator_ref = db.collection("colaborador").stream()

    list_products_select = list()
    list_services_select = list()
    
    async def on_date_change(e):
        
        selected_date = e.control.value
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        nonlocal data_formatada
        # Agora, formate a data no formato 'dia-mes-ano'
        data_formatada = data_objeto.strftime('%d-%m-%Y')    
        
        price_page = _scheduling_.content.controls[13]
        collaborator_select = _scheduling_.collaborator_choose
        service_select = _scheduling_.service_choose
        product_select = _scheduling_.product_choose
        text_price = _scheduling_.price
        button_finish = _scheduling_.button_finish
        
        text_price.content.visible = True
        price_page.visible = True
        collaborator_select.visible = True
        service_select.visible = True
        product_select.visible = True
        button_finish.visible = True
        
        await _scheduling_.update_async()

    def adicionar_dicionario(key, dicionario, lista):
        if key in dicionario and key != "Nenhum":
            produto = dicionario[key]
            lista.append({'nome': produto['nome'], 'preco': produto['preco']})

    def atualizar_visibilidade_widgets(widgets, dicionario, lista):
        total = 0
        for i in range(len(widgets) - 1):
            if widgets[i].content.value:
                key = widgets[i].content.value
                widgets[i + 1].visible = True
                widgets[i + 1].update()
                total += dicionario[key]['preco']
                adicionar_dicionario(key, dicionario, lista)
        return total

    async def widget_visible(e):
        # Obtendo referência dos widgets de serviço e produto
        service_selects = [
            _scheduling_.service_choose,
            _scheduling_.service_choose2,
            _scheduling_.service_choose3,
            _scheduling_.service_choose4,
            _scheduling_.service_choose5
        ]
        
        product_selects = [
            _scheduling_.product_choose,
            _scheduling_.product_choose2,
            _scheduling_.product_choose3,
            _scheduling_.product_choose4,
            _scheduling_.product_choose5,
        ]

        # Obtendo referência aos dicionários de produto e serviço
        product_dict = _scheduling_.product_dict
        service_dict = _scheduling_.service_dict

        # Limpando as listas antes do loop
        list_services_select.clear()
        list_products_select.clear()

        # Atualizando a visibilidade dos widgets e somando preços
        _scheduling_.soma_servico = atualizar_visibilidade_widgets(service_selects, service_dict, list_services_select)
        _scheduling_.soma_produto = atualizar_visibilidade_widgets(product_selects, product_dict, list_products_select)

        # Atualizando o preço total e a UI
        update_price()
        await _scheduling_.update_async()

    async def finish_scheduling(e):

        if not hasattr(_scheduling_, 'soma_servico') or _scheduling_.soma_servico is None:
            await widget_visible()

        if checks_fields():
            # Obtendo referencia dos widget
            # Obtendo valores para salvar no sistema
            collaborator_id = _scheduling_.collaborator_choose.content.value
            price_services = float(_scheduling_.soma_servico)
            price_products = float(_scheduling_.soma_produto)
            price_final = float(
                str(
                    _scheduling_.price.content.value
                    ).replace(',', "."))
            discount = (price_services + price_products) - price_final
            
            create = scheduling_db.CreateService(
                collaborator_id,
                data_formatada,
                list_services_select,
                list_products_select,
                price_services,
                price_products,
                discount,
                price_final)
            
            create.finish_service()
            texto = "Atendimento cadastrado!"
            await transition.main(page, texto, None)

    def update_price():
        # Campo preço na tela
        price_page = _scheduling_.price.content

        # Atualizar o valor total
        total_price = _scheduling_.soma_servico + _scheduling_.soma_produto
        price_page.value = total_price
        price_page.update()

    def checks_fields():
        verifica = 0
        price_page = _scheduling_.price.content
        
        if price_page.value == "":
            price_page.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        elif not converte_float(str(price_page.value).replace(',', ".")):
            price_page.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        elif float(str(price_page.value).replace(',', ".")) == 0.0:
            price_page.border_color = COLOR_BORDER_COLOR_ERROR
            verifica += 1
        
        else:
            price_page.error_text = None
            
        price_page.update()
        return True if verifica == 0 else None

    def converte_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    async def back_button(e):
        page.go("/menu")

    _scheduling_ = UserWidget(
        "Cadastrar Atendimento!",
        product_ref,
        service_ref,
        collaborator_ref,
        finish_scheduling,
        widget_visible,
        back_button,
        on_date_change,
    )
    
    return _scheduling_
