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
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker
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
        scheduling_id,   
        dict_scheduling,
        product_ref,
        service_ref,
        collaborator_ref,
        func1,
        func2,
        func3,
        ):
        super().__init__()
        self.title = title
        self.scheduling_id = scheduling_id
        self.dict_scheduling = dict_scheduling[scheduling_id]
        self.product_ref = product_ref
        self.service_ref = service_ref
        self.collaborator_ref = collaborator_ref
        self.func = func1
        self.func2 = func2
        self.func3 = func3
        
        self.name = self.dict_scheduling['nome']
        self.phone = self.dict_scheduling['telefone']
        self.data = f"{self.dict_scheduling['data']}"
        self.time = self.dict_scheduling['horario']
        self.price_service = self.dict_scheduling['preco_servico']
        self.service = self.dict_scheduling['servico_id']
        self.collaborator_id = self.dict_scheduling['colaborador_id']
        self.data_time = f'{self.data} as {self.time}'
        self.service_dict = {}
        self.product_dict = {}
        self.price_products = 0.0

        self.service_choose = createDropdown("Escolha o Serviço", self.func2, set_value=self.service)
        self.service_choose2 = createDropdown("Escolha o Serviço", self.func2)
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

        self.collaborator_choose = createDropdown("Escolha o(a) atendente", set_value=self.collaborator_id)

        for _collaborator in self.collaborator_ref:
            collaborator = self.collaborator_choose.content
            _collaborator_id = _collaborator.id
            _collaborator_date = _collaborator.to_dict()
            if _collaborator_date['permitir_agendamento']:
                _nome = f'{_collaborator_date["nome"]}'
                collaborator.options.append(ft.dropdown.Option(text= _nome, key=_collaborator_id))
        
        self.product_choose = createDropdown("Escolha outro produto", self.func2)
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
            
        self.price = createInputTextField("Preço total", default_value=self.price_service)

        self.content = self.build()

    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                ft.Column(
                    spacing=12,
                    controls=[
                        createInputTextField("Nome no agendamento!", default_value=self.name, set_read_only=True),
                        createInputTextField("Telefone no agendamento!", default_value=self.phone, set_read_only=True),
                        createInputTextField("Data e hora!", default_value=self.data_time, set_read_only=True),
                    ],
                ),
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
                createSubTitle("Preço total"),
                ft.Column(
                    spacing=0,
                    controls=[
                        self.price,
                    ],
                ),
                ft.Container(padding=3),
                createElevatedButton("Finalizar agendamento", self.func),
                createElevatedButton("Voltar", self.func3),
            ],
        )
    
async def view_finish_scheduling(page: ft.Page):

    stored_user = await loadStoredUser(page)
    stored_scheduling = await loadSchedulingFinish(page)
    # Se não possuir user armazenado retorna para tela home
    if stored_user is None or stored_user['funcaoID'] == "cliente":
        page.go("/")
        view = ft.View()
        return view
    
    if stored_scheduling is None:
        page.go("/")
        view = ft.View()
        return view

    db = get_firestore_client()
    service_ref = db.collection("servico").stream()
    id_scheduling = list(stored_scheduling.keys())[0]

    product_ref = db.collection("produto").stream()
    collaborator_ref = db.collection("colaborador").stream()

    list_services_select = list()
    list_products_select = list()
  
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

    async def widget_visible(e=None):
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
            collaborator_id = _scheduling_.collaborator_choose.content.value
            service_id = _scheduling_.service_choose.content.value
            name_service = _scheduling_.service_dict[service_id]["nome"]
            price_services = float(_scheduling_.soma_servico)
            price_products = float(_scheduling_.soma_produto)
            price_total = float(str(_scheduling_.price.content.value).replace(',', "."))
        
            discount = (price_services + price_products) - price_total

            print("Foi")

            # finish = scheduling_db.FinishScheduling(
            #     id_scheduling,
            #     collaborator_id,
            #     name_service,
            #     service_id,
            #     list_services_select,
            #     list_products_select,
            #     price_services,
            #     price_products,
            #     discount,
            #     price_total)
        
            # finish.finish_scheduling()
            # texto = "Agendamento finalizado!"
            # await tela_transicao.main(page, user, texto)

    def update_price():    
    # def update_price(e):
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

    async def back_button_(e):
        page.go("/menu")

    _scheduling_ = UserWidget(
        "Finalizar agendamento!",
        id_scheduling,
        stored_scheduling,
        product_ref,
        service_ref,
        collaborator_ref,
        finish_scheduling,
        widget_visible,
        back_button_,
    )
    
    return _scheduling_

    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_scheduling_)

    view = ft.View(
        route='/finalizar-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )

    return view