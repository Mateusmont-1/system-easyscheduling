import flet as ft
from google.cloud.firestore_v1 import FieldFilter
import asyncio
import datetime

from views import transition
from utils import register
from utils.validation import validate_fields, length_validator, phone_with_ddd_validator, date_validator, time_validator
from utils.firebase_config import get_firestore_client
from utils.interface import (
    createTitle, createSubTitle, createElevatedButton, 
    createFooterText, createInputTextField, createMainColumn,
    createImageLogo, createDropdown, createDatePickerForScheduling, createCallDatePicker,
    createCheckbox, createDataTable
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO, COLOR_BORDER_COLOR
from utils.client_storage import loadStoredUser, loadSchedulingEdit, removeSchedulingEdit
from utils.scheduling_utils import string_to_time, get_agendamentos, periodo_disponivel, processa_colaborador
from utils.validation import validate_fields, length_validator, converte_float

class UserWidget(ft.Container):
    def __init__(
            self,
        title:str,
        btn_name:str,
        btn_name2:str,
        collaborator_ref,
        func,
        func2,
        func3,
        func4,
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.btn_name2 = btn_name2
        self.collaborator_ref = collaborator_ref
        self.func = func
        self.func2 = func2
        self.func3 = func3
        self.func4 = func4
        self.collaborator_dict = dict()

        self.collaborator_choose = createDropdown("Escolha o(a) atendente", func=self.func)

        for atendente in self.collaborator_ref:
            # Cada documento é um objeto com ID e dados
            atendente_dropdown = self.collaborator_choose.content
            _atendente_data = atendente.to_dict()
            _colaborador_id = atendente.id
            
        
            _nome = _atendente_data['nome']
            
            # adiciona no dropdown o atendente
            atendente_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _colaborador_id,))
            
            self.collaborator_dict[_colaborador_id] = _atendente_data

        self.date_picker = createDatePickerForScheduling(self.func2, set_days=60)
        self.day_choose = createCallDatePicker("Informe o dia", self.date_picker)
        self.query_type = createDropdown("Escolha o tipo de folga", func=self.func, set_visible=False)
        self.day_select = createInputTextField("Data selecionada", set_read_only=True, set_visible=False)
        for i in range(2):
            # Cada documento é um objeto com ID e dados
            query_dropdown = self.query_type.content
            if i < 1:
                texto = "Diário"
            elif i < 2:
                texto = "Semanal"
            # elif i < 3:
            #     texto = "Mensal"
            # adiciona no dropdown o atendente
            query_dropdown.options.append(ft.dropdown.Option(text= texto, key= i))

        self.content = self.build()
    
    def build(self):
        return ft.Column(
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self.collaborator_choose,
                self.query_type,
                self.day_choose,
                self.day_select,
                ft.Container(padding=5),
                createElevatedButton(self.btn_name, self.func4),
                createElevatedButton(self.btn_name2, self.func3),
                ft.Container(padding=10),
                self.date_picker,
            ],
        )
    
async def view_create_day_off(page: ft.Page):
    stored_user = await loadStoredUser(page)

    if stored_user is None:
        page.go("/")
        return ft.View()
    
    elif stored_user['funcaoID'] != "administrador":
        page.go("/menu")
        view = ft.View()
        return view
    
    # Obtém o cliente Firestore e a referência aos colaboradores
    db = get_firestore_client()
    collaborator_ref = db.collection("colaborador").stream()
    
    datas_folga = None

    # Função chamada quando a data é alterada
    def _on_date_change(e=None):
        selected_date = obter_data_selecionada(e)
        collaborator_choose, query_type, data_select = obter_referencias_widgets()
        mes, ano, data_formatada = extrair_mes_ano(selected_date)
        
        # Define as datas de folga conforme o tipo de consulta
        nonlocal datas_folga
        if query_type.value == "0":
            datas_folga = [data_formatada]
            data_select.value = data_formatada
        elif query_type.value == "1":
            datas_folga = obter_dias_da_semana(selected_date)
            data_select.value = ", ".join(datas_folga)
        
        data_select.visible = True
        data_select.update()
        return collaborator_choose, datas_folga
    
    # Função para cadastrar as folgas
    async def _cadastrar(e):
        if verifica_campos():
            collaborator_choose, query_type, data_select = obter_referencias_widgets()
            nonlocal datas_folga
            colaborador_id = collaborator_choose.value
            
            # Adiciona as datas de folga para o colaborador
            leave_manager = register.CollaboratorLeaveManager(colaborador_id)
            confirma = leave_manager.adicionar_datas_folga(datas_folga)
            if confirma:
                texto = "Folga cadastrada!"
                await transition.main(page, texto, None)
            else:
                data_select.border_color = COLOR_BORDER_COLOR_ERROR
                data_select.update()

    # Obtém a data selecionada no date_picker ou no evento
    def obter_data_selecionada(e):
        if e:
            return e.control.value
        return _day_off_.date_picker.content.value

    # Obtém referências aos widgets necessários
    def obter_referencias_widgets():
        collaborator_choose = _day_off_.collaborator_choose.content
        query_type = _day_off_.query_type.content
        data_select = _day_off_.day_select.content
        return collaborator_choose, query_type, data_select

    # Extrai o mês, ano e data formatada de uma data fornecida
    def extrair_mes_ano(selected_date):
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        data_formatada = data_objeto.strftime('%d-%m-%Y')
        return data_objeto.month, data_objeto.year, data_formatada

    # Obtém os dias da semana a partir de uma data fornecida
    def obter_dias_da_semana(selected_date):
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        inicio_semana = data_objeto - datetime.timedelta(days=data_objeto.weekday())
        dias_semana = [(inicio_semana + datetime.timedelta(days=i)).strftime('%d-%m-%Y') for i in range(7)]
        return dias_semana

    # Função para atualizar a visibilidade dos widgets
    async def _visible_button(e):
        query_type = _day_off_.query_type
        day_choose = _day_off_.day_choose
        
        if not query_type.visible:
            query_type.visible = True
            query_type.update()
        else:
            day_choose.content.text = "Informe o dia" if query_type.content.value == "0" else "Informe a semana"
            day_choose.visible = True
            day_choose.update()

        if _day_off_.date_picker.content.value is not None:
            _on_date_change()

    # Verifica se os campos estão preenchidos corretamente
    def verifica_campos():
        collaborator_choose, query_type, data_select = obter_referencias_widgets()
        campos = [
            (collaborator_choose, collaborator_choose.value),
            (query_type, query_type.value),
            (data_select, data_select.value),
        ]
        
        campos_invalidos = False
        for campo, valor in campos:
            if not valor:  # Verifica se o valor está vazio ou None
                campo.border_color = COLOR_BORDER_COLOR_ERROR
                campo.update()
                campos_invalidos = True
            else:
                campo.border_color = COLOR_BORDER_COLOR
                campo.update()
        
        return not campos_invalidos

    # Função para retornar ao menu principal
    async def back_button(e):
        page.go("/menu")

    _day_off_ = UserWidget(
        "Cadastrar folga!",
        "Cadastrar",
        "Voltar",
        collaborator_ref,
        _visible_button,
        _on_date_change,
        back_button,
        _cadastrar,
    )

    return _day_off_
