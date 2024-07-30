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
    createImageLogo, createDropdown, createDatePickerForReport, createCallDatePicker,
    createDataTable
)
from utils.config import COLOR_BORDER_COLOR_ERROR, IMG_LOGO, COLOR_TEXT_IN_FIELD
from utils.encrypt import encryptUser
from utils.client_storage import loadStoredUser, setSchedulingFinish
from utils import whatsapp
from utils.whatsapp import TELEFONE_CONTACT
from utils import scheduling_db

class UserWidget(ft.Container):
    def __init__(
        self,
        title:str,
        btn_name:str,
        collaborator_ref,
        func1,
        func2,
        func3
        ):
        super().__init__()
        self.title = title
        self.btn_name = btn_name
        self.collaborator_ref = collaborator_ref
        self.func = func1
        self.func2 = func2
        self.func3 = func3
        
        self.collaborator_dict = dict()
        self.collaborator_choose = createDropdown("Escolha o(a) atendente", self.func)
        self.query_type = createDropdown("Escolha o tipo de consulta", self.func, False)
        self.data_table = createDataTable(False, ["Data", "Nome do atendente", "Valor (R$)"])
        self.date_picker = createDatePickerForReport(self.func2)
        self.day_choose = createCallDatePicker("Escolha o dia", self.date_picker)
        self.no_scheduling = createTitle("Não possui entradas", False)

        for colaborador in self.collaborator_ref:
            # Cada documento é um objeto com ID e dados
            colaborador_dropdown = self.collaborator_choose.content
            _colaborador_id = colaborador.id
            _colaborador_data = colaborador.to_dict()
        
            _nome = _colaborador_data['nome']
            
            # adiciona no dropdown o atendente
            colaborador_dropdown.options.append(ft.dropdown.Option(text= _nome, key= _colaborador_id,))

            self.collaborator_dict[_colaborador_id] = _colaborador_data

        for i in range(3):
            # Cada documento é um objeto com ID e dados
            query_dropdown = self.query_type.content
            if i < 1:
                texto = "Diário"
            elif i < 2:
                texto = "Semanal"
            elif i < 3:
                texto = "Mensal"
            # adiciona no dropdown o atendente
            query_dropdown.options.append(ft.dropdown.Option(text= texto, key= i))
        
        self.content = self.build()

    def build(self):
        return ft.Column(
            scroll="hidden",
            horizontal_alignment="center",
            controls=[
                createTitle(self.title),
                self.collaborator_choose,
                self.query_type,
                self.day_choose,
                ft.Container(padding=3),
                self.data_table,
                self.date_picker,
                self.no_scheduling,
                createElevatedButton(self.btn_name, self.func3),
            ],
        )
    
async def view_check_report_collaborator(page: ft.Page):
    
    stored_user = await loadStoredUser(page)
    # Se não possuir user armazenado retorna para tela home
    if stored_user is None:
        page.go("/")
        view = ft.View()
        return view
    elif stored_user['funcaoID'] == "cliente":
        page.go("/menu")
        view = ft.View()
        return view

    id_finish = ""
    
    db = get_firestore_client()
    collaborator_ref = db.collection("colaborador").stream()
    
    def _visible_button(e):
        dropdown = e.control.value
        query_type = _report_.query_type
        day_choose = _report_.day_choose
        if query_type.visible == False:
            query_type.visible = True
            query_type.update()
        else:
            if query_type.content.value == "0":
                day_choose.content.text = "Informe o dia"
            elif query_type.content.value == "1":
                day_choose.content.text = "Informe a semana"
            if query_type.content.value == "2":
                day_choose.content.text = "Informe o mês"
            day_choose.visible = True
            day_choose.update()

        if _report_.date_picker.content.value != None:
            _on_date_change()
    
    def show_details(row_data, id):
        nonlocal id_finish
        agendamento_id = row_data['agendamento_id']
        agendamento_ref = db.collection('agendamentos').document(agendamento_id).get()
        agendamento_data = agendamento_ref.to_dict()
       # Criação da lista de controles padrão
        controls = [
            ft.Text(f"Nome cliente: {agendamento_data.get('nome', 'N/A')}"),
            ft.Text(f"Data: {row_data['data']}"),
            ft.Text(f"Hórario: {agendamento_data.get('horario', 'N/A')}"),
            ft.Text(f"Preço serviços: R$ {row_data['preco_servico']}"),
            ft.Text(f"Preço produtos: R${row_data['preco_produtos']}"),
            ft.Text(f"Valor Total: R$ {row_data['total']}")
        ]
        # Se tiver desconto aparece no dialog
        if agendamento_data['desconto'] != 0.0:
            controls.append(ft.Text(f"Desconto: R$ {row_data['desconto']}"))
        
        # Adicionando uma linha vazia
        controls.append(ft.Text(""))
        # Verifica se há produtos e adiciona mais controles se necessário
        if 'servicos' in agendamento_data and len(agendamento_data['servicos']) > 0:
            controls.append(ft.Text("Serviços:"))
            for servico in agendamento_data['servicos']:
                controls.append(ft.Text(f" - {servico['nome']}: R$ {servico['preco']}"))

        # Adicionando uma linha vazia
        controls.append(ft.Text(""))
        # Verifica se há produtos e adiciona mais controles se necessário
        if 'produtos' in agendamento_data and len(agendamento_data['produtos']) > 0:
            controls.append(ft.Text("Produtos:"))
            for produto in agendamento_data['produtos']:
                controls.append(ft.Text(f" - {produto['nome']}: R$ {produto['preco']}"))

        dialog.content.controls = controls
        dialog.open = True
        id_finish = id
        page.update()

    id_finish = None
    # Criar o diálogo uma vez
    dialog = ft.AlertDialog(
        title=ft.Text("Detalhes da Receita"),
        content=ft.Column([]),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: close_dialog()),
        ]
    )

    def close_dialog():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)
    # page.dialog = dialog

    # Função principal que é chamada na alteração da data ou do atendente
    def _on_date_change(e=None):
        selected_date = obter_data_selecionada(e)
        collaborator_choose, query_type, data_table = obter_referencias_widgets()
        limpar_tabela(data_table)
        mes, ano, data_formatada= extrair_mes_ano(selected_date)
        lista_transacoes = consultar_transacoes(ano, mes, collaborator_choose.value, query_type.value, data_formatada)
        lista_transacoes.sort(key=lambda x: datetime.datetime.strptime(x.to_dict().get('data', '01-01-1970'), '%d-%m-%Y'))
        atualizar_interface(lista_transacoes, data_table)

    # Obtém a data selecionada no date_picker ou no evento
    def obter_data_selecionada(e):
        if e:
            return e.control.value
        return _report_.date_picker.content.value

    # Obtém referências aos widgets barber_choose e data_table
    def obter_referencias_widgets():
        collaborator_choose = _report_.collaborator_choose.content
        query_type = _report_.query_type.content
        data_table = _report_.data_table.content
        return collaborator_choose, query_type, data_table

    # Limpa as linhas da tabela de dados
    def limpar_tabela(data_table):
        data_table.controls[0].rows.clear()
        data_table.update()

    # Extrai o mês e ano de uma data fornecida
    def extrair_mes_ano(selected_date):
        data_objeto = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')
        data_formatada = data_objeto.strftime('%d-%m-%Y')
        return data_objeto.month, data_objeto.year, data_formatada

    # Consulta as transações no Firestore para o mês, ano e atendente selecionado
    def consultar_transacoes(ano, mes, colaborador_id, query_type, data_formatada):
        transacoes_ref = db.collection("transacoes").document(str(ano)).collection(str(mes).zfill(2))
        if query_type == "0":
            # Consulta para ganhos diários
            query = transacoes_ref.where(filter=FieldFilter("colaborador_id", "==", colaborador_id)).where(filter=FieldFilter("data", "==", data_formatada))
            transacoes = query.stream()
            return list(transacoes)
        
        elif query_type == "1":
            # Consulta para ganhos semanais
            data = datetime.datetime.strptime(data_formatada, "%d-%m-%Y")
            start_of_week = data - datetime.timedelta(days=data.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            transacoes = []
        
            for i in range(7):
                day = start_of_week + datetime.timedelta(days=i)
                day_str = day.strftime("%d-%m-%Y")
                daily_query = transacoes_ref.where(filter=FieldFilter("colaborador_id", "==", colaborador_id)).where(filter=FieldFilter("data", "==", day_str))
                daily_transacoes = daily_query.stream()
                transacoes.extend(list(daily_transacoes))
                
            return transacoes
        
        elif query_type == "2":
            query = transacoes_ref.where(filter=FieldFilter("colaborador_id", "==", colaborador_id))
            transacoes = query.stream()
            return list(transacoes)
        
        else:
            raise ValueError(f"Tipo de consulta {query_type} inválido")
        

    # Atualiza a interface com os dados das transações e o total ganho
    def atualizar_interface(lista_transacoes, data_table):
        if len(lista_transacoes) != 0:
            exibir_tabela()
            total_ganho_servico = 0
            total_ganho_produto = 0
            for transacao in lista_transacoes:
                ganho_servico, ganho_produto = adicionar_transacao_na_tabela(transacao, data_table)
                total_ganho_servico += ganho_servico
                total_ganho_produto += ganho_produto
            total_ganho = total_ganho_servico + total_ganho_produto
            if total_ganho > 0:
                exibir_total_ganho(total_ganho_servico, total_ganho_produto, total_ganho, data_table)
            verificar_tabela_vazia(data_table)
        else:
            ocultar_tabela()

    # Exibe a tabela e oculta o texto "Não possui transações"
    def exibir_tabela():
        _report_.data_table.visible = True
        _report_.data_table.update()
        _report_.no_scheduling.visible = False
        _report_.no_scheduling.update()

    # Adiciona uma transação à tabela de dados
    def adicionar_transacao_na_tabela(transacao, data_table):
        transacao_id = transacao.id
        transacao_data = transacao.to_dict()

        # Valor total cobrado ao cliente
        valor_total = transacao_data.get('total', 0)

        # Valores do serviço
        preco_servico = transacao_data.get('preco_servico', 0)
        desconto = transacao_data.get('desconto', 0)
        ganho_servico = preco_servico - desconto if desconto else preco_servico

        # Valores do produto
        preco_produto = transacao_data.get('preco_produtos', 0)
        ganho_produto = preco_produto

        collaborator = transacao_data.get('colaborador_id', 'N/A')
        name_collaborator = _report_.collaborator_dict[collaborator]['nome']

        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(transacao_data.get('data', 'N/A'),
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(name_collaborator,
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {valor_total:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ],
            on_select_changed=lambda e, transacao=transacao_data, transacao_id=transacao_id: show_details(transacao, transacao_id)
        ))

        return ganho_servico, ganho_produto

    # Exibe o total ganho pelo atendente no mês selecionado
    def exibir_total_ganho(total_ganho_servico, total_ganho_produto, total_ganho, data_table):
        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("")),
            ft.DataCell(ft.Text("")),
            ft.DataCell(ft.Text("")),
        ]))

        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Total Serviços",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text("",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {total_ganho_servico:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ]))

        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Total Produtos",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text("",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {total_ganho_produto:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ]))

        data_table.controls[0].rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text("Total",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text("",
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
            ft.DataCell(ft.Text(f'R$ {total_ganho:.2f}',
                                    text_align="center",
                                    weight="bold",
                                    color=COLOR_TEXT_IN_FIELD)),
        ]))

        data_table.update()

    # Verifica se a tabela está vazia e atualiza a visibilidade dos componentes
    def verificar_tabela_vazia(data_table):
        if len(data_table.controls[0].rows) == 0:
            ocultar_tabela()

    # Oculta a tabela e exibe o texto "Não possui transações"
    def ocultar_tabela():
        _report_.data_table.visible = False
        _report_.data_table.update()
        _report_.no_scheduling.visible = True
        _report_.no_scheduling.update()
    
    async def _back_button(e):
        page.go('/menu')

    _report_ = UserWidget(
        "Receitas colaborador!",
        "Voltar",
        collaborator_ref,
        _visible_button,
        _on_date_change,
        _back_button,
    )
    
    return _report_
    _scheduling_main = createMainColumn(page)
    _scheduling_main.content.controls.append(ft.Container(padding=0))
    _scheduling_main.content.controls.append(_report_)

    view = ft.View(
        route='/verificar-agendamento',
        horizontal_alignment="center",
        vertical_alignment="center",
        controls=[
            _scheduling_main,
        ]
    )

    return view