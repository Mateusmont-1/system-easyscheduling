import json
from flet.security import encrypt, decrypt

from utils.config import SECRET_KEY

def encryptUser(raw):
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY não está configurada!")
    temp = encrypt(json.dumps(raw), SECRET_KEY)
    return temp

def decryptedUser(raw):
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY não está configurada!")
    temp = decrypt(raw, SECRET_KEY)
    return json.loads(temp)



    
        