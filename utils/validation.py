import re
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from utils.config import COLOR_BORDER_COLOR_ERROR, COLOR_BORDER_COLOR

def is_valid_email(email):
    if email is None:
        return False
    try:
        validate_email(email)
        return True
    except EmailNotValidError as ex:
        print(str(ex))
        return False

def validate_fields(fields):
    """
    Valida uma lista de campos.
    fields é uma lista de tuplas (field, validators)
    field: objeto campo
    validators: lista de funções de validação que retornam True se válido, False se inválido
    """
    all_valid = True
    for field, validators in fields:
        is_valid = True
        for validator in validators:
            # Verifica se o campo é um checkbox
            if hasattr(field, 'is_error'):
                value = field.value
            else:
                value = field.content.value

            if value is None or not validator(value):
                is_valid = False
                break

        # Manipula a cor de acordo com o tipo de campo
        if hasattr(field, 'is_error'):
            field.is_error = not is_valid
        else:
            field.content.border_color = COLOR_BORDER_COLOR if is_valid else COLOR_BORDER_COLOR_ERROR
        field.update()

        if not is_valid:
            all_valid = False

    return all_valid

def min_length_validator(min_length):
    def validate(value):
        if value is None:
            return False
        return len(value) >= min_length
    return validate

def max_length_validator(max_length):
    def validate(value):
        if value is None:
            return False
        return len(value) <= max_length
    return validate

def length_validator(min_length, max_length):
    def validate(value):
        if value is None:
            return False
        return min_length <= len(value) <= max_length
    return validate

def ddd_validator(value):
    if value is None:
        return False
    return re.match(r'^\d{2}$', value) is not None

def phone_validator(value):
    if value is None:
        return False
    value = value.replace("-", "")
    return re.match(r'^\d{8,9}$', value) is not None

def phone_with_ddd_validator(value):
    if value is None:
        return False
    value = value.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
    return re.match(r'^\d{10,11}$', value) is not None

def checkbox_validator(value):
    return value

def date_validator(value):
    if value is None:
        return False
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def time_validator(value):
    if value is None:
        return False
    try:
        datetime.strptime(value, '%H:%M')
        return True
    except ValueError:
        return False

def converte_float(value):
    """
    Converte uma string em float se possível.
    Retorna True se a conversão for bem-sucedida, caso contrário, False.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False