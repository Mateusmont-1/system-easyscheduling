from firebase_admin import db
from datetime import datetime, timedelta
from google.cloud.firestore_v1 import FieldFilter
import requests
import os
import time
from functools import lru_cache
import httpx


from .logger import logger
from .firebase_config import get_firestore_client, cred
from .config import FLET_PATH, API_URL

async def register_barbearia():
    start_time = time.time()
    data = {
        "flet_path": FLET_PATH.replace("/", ""),
        "cred": {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "aunt_provider_x509_cert_url": os.getenv("FIREBASE_AUNT_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
        }
    }
    # Usando httpx para fazer a requisição POST de forma assíncrona
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/register", json=data)

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução de register_barbearia: {elapsed_time:.4f} segundos")

    return response.json()

async def get_colaborador_cache(colaborador_id=None):
    async with httpx.AsyncClient() as client:
        start_time = time.time()

        # Garantir que a URL sempre inclua o protocolo
        url = f"{API_URL}/cache{FLET_PATH}/{colaborador_id}"if colaborador_id else f"{API_URL}/cache{FLET_PATH}"
        print(url)
        response = await client.get(url)  # Executa a requisição de forma assíncrona

        elapsed_time = time.time() - start_time
        print(f"Tempo de execução de get_colaborador_cache: {elapsed_time:.4f} segundos")
        return response.json()  # Decodifica a resposta JSON
    
# # Exemplo de como recuperar cache de um colaborador
# async def get_colaborador_cache(colaborador_id=None):
#     start_time = time.time()
#     if colaborador_id is None:
#         response = requests.get(f"{API_URL}/cache{FLET_PATH}")
#     else:
#         response = requests.get(f"{API_URL}/cache{FLET_PATH}/{colaborador_id}")

#     elapsed_time = time.time() - start_time
#     print(f"Tempo de execução de get_colaborador_cache: {elapsed_time:.4f} segundos")
#     return response.json()


# @lru_cache(maxsize=128)
# def register_barbearia():
#     start_time = time.time()

#     data = {
#         "flet_path": FLET_PATH.replace("/", ""),
#         "cred": {
#             "type": os.getenv("FIREBASE_TYPE"),
#             "project_id": os.getenv("FIREBASE_PROJECT_ID"),
#             "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
#             "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
#             "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
#             "client_id": os.getenv("FIREBASE_CLIENT_ID"),
#             "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
#             "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
#             "aunt_provider_x509_cert_url": os.getenv("FIREBASE_AUNT_PROVIDER_X509_CERT_URL"),
#             "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
#             "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
#         }
#     }
#     response = requests.post(f"{API_URL}/register", json=data)
    
#     elapsed_time = time.time() - start_time
#     print(f"Tempo de execução de register_barbearia: {elapsed_time:.4f} segundos")
    
#     return response.json()

# # async def get_colaborador_cache(colaborador_id=None):
# #     start_time = time.time()
    
# #     url = f"{API_URL}/cache{FLET_PATH}"
# #     if colaborador_id:
# #         url += f"/{colaborador_id}"
# #     response = requests.get(url)
    
# #     elapsed_time = time.time() - start_time
# #     print(f"Tempo de execução de get_colaborador_cache (colaborador_id={colaborador_id}): {elapsed_time:.4f} segundos")
    
# #     return response.json()






# db = get_firestore_client()

# def get_all_collaborator_ids():
#     collaborator_ids = []
#     collaborators_ref = db.collection("colaborador")
#     collaborators = collaborators_ref.stream()
    
#     for collaborator in collaborators:
#         collaborator_ids.append(collaborator.id)
    
#     return collaborator_ids

# # Função para salvar o cache no Firestore
# def save_cache_to_firestore(cache_data):
#     # Verifica se todos os IDs de colaboradores estão presentes no cache
#     all_collaborator_ids = get_all_collaborator_ids()
    
#     for colaborador_id in all_collaborator_ids:
#         if colaborador_id not in cache_data:
#             cache_data[colaborador_id] = {
#                 "daily_revenue": 0,
#                 "daily_transactions": 0,
#                 "weekly_revenue": 0,
#                 "weekly_transactions": 0,
#                 "last_update": datetime.now()
#             }

#     print(cache_data)
    
#     cache_ref = db.collection("cache").document("revenue_cache")
#     cache_ref.set(cache_data)

# # # Função para salvar o cache no Firestore
# # def save_cache_to_firestore(cache_data):
# #     cache_ref = db.collection("cache").document("revenue_cache")
# #     cache_ref.set(cache_data)

# # Variável global para armazenar o cache localmente
# local_cache = None

# # Função para carregar o cache do Firestore apenas uma vez
# def load_cache_from_firestore():
#     global local_cache
#     if local_cache is None:
#         cache_ref = db.collection("cache").document("revenue_cache")
#         cache_doc = cache_ref.get()
#         if cache_doc.exists:
#             local_cache = cache_doc.to_dict()
#         else:
#             local_cache = {}
#     return local_cache

# # Função para calcular a receita diária por colaborador com totalizador de transações
# def calculate_daily_revenue():
#     now = datetime.now()
#     data_formatada = now.strftime('%d-%m-%Y')
#     ano = now.year
#     mes = now.month
    
#     transacoes_ref = db.collection("transacoes").document(str(ano)).collection(str(mes).zfill(2))
#     query = transacoes_ref.where(filter=FieldFilter("data", "==", data_formatada))
#     transactions = query.stream()

#     daily_revenue = {}

#     for transaction in transactions:
#         data = transaction.to_dict()
#         colaborador_id = data['colaborador_id']
#         total = data['total']
        
#         if colaborador_id not in daily_revenue:
#             daily_revenue[colaborador_id] = {"total_value": 0, "total_transactions": 0}
        
#         daily_revenue[colaborador_id]["total_value"] += total
#         daily_revenue[colaborador_id]["total_transactions"] += 1
    
#     return daily_revenue

# # Função para calcular a receita semanal por colaborador com totalizador de transações
# def calculate_weekly_revenue():
#     now = datetime.now()

#     # Calcular a data de início e fim da semana atual
#     start_of_week = now - timedelta(days=now.weekday())  # Segunda-feira
#     end_of_week = start_of_week + timedelta(days=6)  # Domingo

#     weekly_revenue = {}

#     # Iterar por cada dia da semana atual
#     current_day = start_of_week
#     while current_day <= end_of_week:
#         data_formatada = current_day.strftime('%d-%m-%Y')
#         mes_atual = current_day.month
#         ano_atual = current_day.year

#         transacoes_ref = db.collection("transacoes").document(str(ano_atual)).collection(str(mes_atual).zfill(2))
#         query = transacoes_ref.where(filter=FieldFilter("data", "==", data_formatada))
#         transactions = query.stream()

#         for transaction in transactions:
#             data = transaction.to_dict()
#             colaborador_id = data['colaborador_id']
#             total = data['total']
            
#             if colaborador_id not in weekly_revenue:
#                 weekly_revenue[colaborador_id] = {"total_value": 0, "total_transactions": 0}
            
#             weekly_revenue[colaborador_id]["total_value"] += total
#             weekly_revenue[colaborador_id]["total_transactions"] += 1

#         current_day += timedelta(days=1)  # Próximo dia
    
#     return weekly_revenue

# # Listener para alterações na coleção 'transacoes'
# def on_transaction_update(doc_snapshot, changes, read_time):
#     cache = load_cache_from_firestore()
#     print("Alteração detectada no Firestore.")
    
#     # Recalcula e atualiza o cache apenas para colaboradores com transações
#     daily_revenue = calculate_daily_revenue()
#     weekly_revenue = calculate_weekly_revenue()
    
#     for colaborador_id in weekly_revenue:
#         cache[colaborador_id] = {
#             "daily_revenue": daily_revenue[colaborador_id]["total_value"],
#             "daily_transactions": daily_revenue[colaborador_id]["total_transactions"],
#             "weekly_revenue": weekly_revenue.get(colaborador_id, {"total_value": 0})["total_value"],
#             "weekly_transactions": weekly_revenue.get(colaborador_id, {"total_transactions": 0})["total_transactions"],
#             "last_update": datetime.now()
#         }

#     # Salvar o cache atualizado no Firestore
#     save_cache_to_firestore(cache)

# # Configurando o listener
# def start_transaction_listener():
#     now = datetime.now()
#     ano = now.year
#     mes = now.month
#     transacoes_ref = db.collection("transacoes").document(str(ano)).collection(str(mes).zfill(2))
#     transacoes_ref.on_snapshot(on_transaction_update)

# # Função para recuperar receita do cache por colaborador
# def get_revenue_from_cache(colaborador_id=None):
#     cache = load_cache_from_firestore()
#     now = datetime.now()

#     print(colaborador_id)

#     # Verifica se o colaborador_id está na lista de IDs de colaboradores válidos
#     if colaborador_id is None:
#         # Se colaborador_id for None, retorna o total diário e semanal de todos os colaboradores
#         total_daily_value = sum(data["daily_revenue"] for data in cache.values())
#         total_weekly_value = sum(data["weekly_revenue"] for data in cache.values())
#         total_daily_transactions = sum(data["daily_transactions"] for data in cache.values())
#         total_weekly_transactions = sum(data["weekly_transactions"] for data in cache.values())
#         return total_daily_value, total_weekly_value, total_daily_transactions, total_weekly_transactions

#     else:

#         if colaborador_id not in get_all_collaborator_ids():
#             print("Aqui")
#             # Se o colaborador_id não for de um colaborador, retorna valores zerados sem forçar a atualização do cache
#             return 0, 0, 0, 0

#         # Se o cache estiver vazio ou desatualizado para esse colaborador, recalcular
#         if not cache or cache.get(colaborador_id, {}).get("last_update") is None:
#             daily_revenue = calculate_daily_revenue()
#             weekly_revenue = calculate_weekly_revenue()
#             print("Passou aqui")
            
#             # Atualizar o cache apenas para colaboradores com transações
#             for colaborador in daily_revenue:
#                 cache[colaborador] = {
#                     "daily_revenue": daily_revenue[colaborador]["total_value"],
#                     "daily_transactions": daily_revenue[colaborador]["total_transactions"],
#                     "weekly_revenue": weekly_revenue.get(colaborador, {"total_value": 0})["total_value"],
#                     "weekly_transactions": weekly_revenue.get(colaborador, {"total_transactions": 0})["total_transactions"],
#                     "last_update": now
#                 }
            
#             # Salvar o cache atualizado no Firestore
#             save_cache_to_firestore(cache)

#         # Retorna a receita e total de transações específicas do colaborador
#         colaborador_cache = cache.get(colaborador_id, {})
#         return (
#             colaborador_cache.get("daily_revenue", 0),
#             colaborador_cache.get("weekly_revenue", 0),
#             colaborador_cache.get("daily_transactions", 0),
#             colaborador_cache.get("weekly_transactions", 0)
#         )