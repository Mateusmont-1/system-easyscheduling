import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()
TELEFONE_CONTACT = os.getenv("TELEFONE_CONTACT")
CONTACT_NAME = os.getenv("CONTACT_NAME")

class MessageSender:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        # self.api_key = os.environ.get('API_KEY')
        self.send_message_url = "http://whatsapp_web_api:3000/client/sendMessage/f8377d8d-a589-4242-9ba6-9486a04ef80c"
        self.check_number_url = "http://whatsapp_web_api:3000/client/getNumberId/f8377d8d-a589-4242-9ba6-9486a04ef80c"
        self.headers = {
            'accept': '*/*',
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def clean_phone_number(self, telefone):
        try:
            return re.sub(r'\D', '', telefone)
        except Exception as e:
            print(f"Erro ao limpar número de telefone: {e}")
            return None

    def check_number(self, telefone):
        try:
            cleaned_phone = self.clean_phone_number(telefone)
            payload = {"number": f"55{cleaned_phone}"}
            response = requests.post(self.check_number_url, headers=self.headers, json=payload)
            response_data = response.json()
            if response_data.get("success") and "result" in response_data and "_serialized" in response_data["result"]:
                return response_data["result"]["_serialized"]
        except Exception as e:
            print(f"Erro ao verificar número: {e}")
        return None

    def create_message(self, name_user, day, hour, name_collaborator, message_type):
        if message_type == "novo_agendamento":
            return f"""*Mensagem automática*

Olá {name_user},
    
O seu agendamento para o dia *{day} às {hour}* com o(a) {name_collaborator},
Foi agendado com sucesso.

Por favor, tente chegar 10 minutos antes do horário marcado. Temos uma tolerância de 10 minutos de atraso.

Para qualquer informação ou alteração, entre em contato com o número abaixo.

Atenciosamente,
*Sistema EasyScheduling*"""
        elif message_type == "update":
            return f"""*Mensagem automática*

Olá {name_user},
    
O seu agendamento foi atualizado para o dia *{day} às {hour}* com o(a) {name_collaborator}.

Por favor, tente chegar 10 minutos antes do horário marcado. Temos uma tolerância de 10 minutos de atraso.

Para qualquer informação ou alteração, entre em contato com o número abaixo.

Atenciosamente,
*Sistema EasyScheduling*"""
        elif message_type == "cancel":
            return f"""*Mensagem automática*

Olá {name_user},
    
O seu agendamento para o dia *{day} às {hour}* com o(a) {name_collaborator} foi cancelado.

Para qualquer informação ou alteração, entre em contato com o número abaixo.

Atenciosamente,
*Sistema EasyScheduling*"""
        else:
            return "Tipo de mensagem inválido."

    def send_message(self, telefone, name_user, day, hour, name_collaborator, message_type):
        try:
            serialized_phone = self.check_number(telefone)
            if not serialized_phone:
                return {"error": "Número de telefone não possui WhatsApp ou não é válido."}
            texto = self.create_message(name_user, day, hour, name_collaborator, message_type)
            payload = {
                "chatId": serialized_phone,
                "contentType": "string",
                "content": texto
            }
            response = requests.post(self.send_message_url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return None
    
    def send_contact(self, telefone_user, telefone_contact):
        try:
            serialized_phone_user = self.check_number(telefone_user)
            if not serialized_phone_user:
                return {"error": "Número de telefone do usuário não possui WhatsApp ou não é válido."}
            serialized_phone_contact = self.check_number(telefone_contact)
            if not serialized_phone_contact:
                return {"error": "Número de telefone do contato não possui WhatsApp ou não é válido."}
            payload = {
                "chatId": serialized_phone_user,
                "contentType": "Contact",
                "content": {"contactId": serialized_phone_contact}
            }
            response = requests.post(self.send_message_url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Erro ao enviar contato: {e}")
            return None

# Exemplo de uso:
# mensagem = MessageSender()
# mensagem_enviada = mensagem.send_message(phone.value, name.value, day_choose, hour_choose.value, colaborador_disponivel[collaborator_choose.value]['nome'], "novo_agendamento")
# mensagem_contato = mensagem.send_contact(phone.value, TELEFONE_CONTACT)
