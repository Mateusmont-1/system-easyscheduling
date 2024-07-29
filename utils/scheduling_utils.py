import datetime
import asyncio
from flet import Page
from firebase_admin.firestore import FieldFilter
from utils.firebase_config import get_firestore_client

def string_to_time(time_str):
    return datetime.datetime.strptime(time_str, '%H:%M')

def get_agendamentos(db, data_desejada):
    agendamentos_ref = db.collection('agendamentos')
    query = agendamentos_ref.where(
                filter=FieldFilter('data', "==", data_desejada)
            ).where(
                filter=FieldFilter('status_agendamento', 'in', ['Concluido', 'Em andamento'])
            ).stream()
    
    agendamentos = {}
    for agendamento in query:
        agendamento_data = agendamento.to_dict()
        agendamento_data['id'] = agendamento.id  # Inclui a ID do documento
        colaborador_id = agendamento_data['colaborador_id']
        if colaborador_id not in agendamentos:
            agendamentos[colaborador_id] = []
        agendamentos[colaborador_id].append(agendamento_data)
    
    return agendamentos

def periodo_disponivel(inicio, fim, agendamentos, agendamento_id=None):
    for agendamento_data in agendamentos:
        horario_agendado_str = agendamento_data.get('horario')
        if horario_agendado_str:
            horario_agendado = string_to_time(horario_agendado_str)
            duracao_agendada = datetime.timedelta(minutes=int(agendamento_data['duracao_servico']))
            fim_agendado = horario_agendado + duracao_agendada
            if inicio < fim_agendado and fim > horario_agendado:
                if agendamento_id and 'id' in agendamento_data and agendamento_data['id'] == agendamento_id:
                    return True  # Ignorar o agendamento atual
                return False
    return True

async def processa_colaborador(colaborador, data_formatada, dia_atual, mes_atual, hora_atual, duracao_servico, agendamentos, colaboradores_disponivel, horario_disponivel, agendamento_id=None):
    dados = colaborador.to_dict()
    dias_folga = dados.get('dias_folga', [])
    dias_trabalhados = dados.get('dias_trabalhados', [0, 1, 2, 3, 4, 5, 6])
    if dados['permitir_agendamento'] and data_formatada not in dias_folga:
        id = colaborador.id
        dia, mes, ano = map(int, data_formatada.split("-"))
        data = datetime.date(year=ano, month=mes, day=dia)
        dia_semana = data.weekday()
        if dia_semana not in dias_trabalhados:
            return
        horarios_disponiveis = dados['dias_uteis'] if dia_semana < 5 else dados['sabado'] if dia_semana == 5 else dados['domingo']
        for hora in horarios_disponiveis:
            if len(horarios_disponiveis) <= 1 or (dia == dia_atual and mes == mes_atual and hora < hora_atual):
                continue
            inicio_servico = string_to_time(hora)
            fim_servico = inicio_servico + duracao_servico
            if periodo_disponivel(inicio_servico, fim_servico, agendamentos.get(id, []), agendamento_id):
                if id not in colaboradores_disponivel:
                    colaboradores_disponivel[id] = {"nome": dados["nome"], "horarios_disponivel": []}
                colaboradores_disponivel[id]["horarios_disponivel"].append(hora)
                if hora not in horario_disponivel:
                    horario_disponivel.append(hora)
                    horario_disponivel.sort()