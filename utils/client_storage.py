import flet as ft
from datetime import datetime, timedelta

from utils.encrypt import encryptUser, decryptedUser
from utils.config import FLET_PATH
from utils import login

async def setUser(page: ft.Page, encrypted_user):
    await page.client_storage.set_async(f"user{FLET_PATH}", encrypted_user)

async def getUser(page: ft.Page):
    return await page.client_storage.get_async(f"user{FLET_PATH}")

async def removeUser(page: ft.Page):
    user = await getUser(page)
    if user is not None:
        await page.client_storage.remove_async(f"user{FLET_PATH}")

async def setEmail(page: ft.Page, email):
    await page.client_storage.set_async(f"email{FLET_PATH}", email)

async def getEmail(page: ft.Page):
    return await page.client_storage.get_async(f"email{FLET_PATH}")

async def removeEmail(page: ft.Page):
    email = await getEmail(page)
    if email is not None:
        await page.client_storage.remove_async(f"email{FLET_PATH}")

async def setSchedulingEdit(page: ft.Page, scheduling):
    await page.client_storage.set_async(f"scheduling{FLET_PATH}", scheduling)

async def getSchedulingEdit(page: ft.Page):
    return await page.client_storage.get_async(f"scheduling{FLET_PATH}")

async def removeSchedulingEdit(page: ft.Page):
    scheduling = await getSchedulingEdit(page)
    if scheduling is not None:
        await page.client_storage.remove_async(f"scheduling{FLET_PATH}")

async def setSchedulingFinish(page: ft.Page, scheduling):
    await page.client_storage.set_async(f"schedulingfinish{FLET_PATH}", scheduling)

async def getSchedulingFinish(page: ft.Page):
    return await page.client_storage.get_async(f"schedulingfinish{FLET_PATH}")

async def removeSchedulingFinish(page: ft.Page):
    scheduling = await getSchedulingFinish(page)
    if scheduling is not None:
        await page.client_storage.remove_async(f"schedulingfinish{FLET_PATH}")

async def setServiceEdit(page: ft.Page, service):
    await page.client_storage.set_async(f"service{FLET_PATH}", service)

async def getServiceEdit(page: ft.Page):
    return await page.client_storage.get_async(f"service{FLET_PATH}")

async def removeServiceEdit(page: ft.Page):
    service = await getServiceEdit(page)
    if service is not None:
        await page.client_storage.remove_async(f"service{FLET_PATH}")

async def setProductEdit(page: ft.Page, service):
    await page.client_storage.set_async(f"product{FLET_PATH}", service)

async def getProductEdit(page: ft.Page):
    return await page.client_storage.get_async(f"product{FLET_PATH}")

async def removeProductEdit(page: ft.Page):
    service = await getProductEdit(page)
    if service is not None:
        await page.client_storage.remove_async(f"product{FLET_PATH}")

async def loadStoredUser(page:ft.page):
    encrypt_stored_user = await getUser(page)
    # Se nao possuir usuario autenticado
    if encrypt_stored_user is None:
        return None
    stored_user = decryptedUser(encrypt_stored_user)
    expiration_time = datetime.strptime(stored_user["expiration_time"], "%Y-%m-%d %H:%M:%S")
    # Se a sessão não expirou retorna o usuario autenticado
    if datetime.now() < expiration_time:
        return stored_user
    
    stored_user = await aunthenticationRefreshtoken(page, stored_user)
    return stored_user

async def aunthenticationRefreshtoken(page: ft.Page, stored_user):
    conta = login.User(stored_user['email'], '')
    conta.refreshToken = stored_user['refreshToken']
    conta.idToken = stored_user['idToken']
    
    if not conta.validate_token():
        await removeUser(page)
        return None

    stored_user['idToken'] = conta.idToken
    stored_user['expiration_time'] = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    encrypted_user = encryptUser(stored_user)
    await setUser(page, encrypted_user)
    return stored_user

async def loadSchedulingEdit(page:ft.page):
    encrypt_scheduling = await getSchedulingEdit(page)
    # Se nao possuir usuario autenticado
    if encrypt_scheduling is None:
        return None
    stored_scheduling = decryptedUser(encrypt_scheduling)
    return stored_scheduling

async def loadSchedulingFinish(page:ft.page):
    encrypt_scheduling = await getSchedulingFinish(page)
    # Se nao possuir usuario autenticado
    if encrypt_scheduling is None:
        return None
    stored_scheduling = decryptedUser(encrypt_scheduling)
    return stored_scheduling

async def loadServiceEdit(page:ft.page):
    encrypt_service = await getServiceEdit(page)
    # Se nao possuir usuario autenticado
    if encrypt_service is None:
        return None
    stored_service = decryptedUser(encrypt_service)
    return stored_service

async def loadProductEdit(page:ft.page):
    encrypt_product = await getProductEdit(page)
    # Se nao possuir usuario autenticado
    if encrypt_product is None:
        return None
    stored_product = decryptedUser(encrypt_product)
    return stored_product

async def setCollaboratorEdit(page: ft.Page, service):
    await page.client_storage.set_async(f"collaborator{FLET_PATH}", service)

async def getCollaboratorEdit(page: ft.Page):
    return await page.client_storage.get_async(f"collaborator{FLET_PATH}")

async def removeCollaboratorEdit(page: ft.Page):
    collaborator = await getCollaboratorEdit(page)
    if collaborator is not None:
        await page.client_storage.remove_async(f"collaborator{FLET_PATH}")

async def loadCollaboratorEdit(page:ft.page):
    encrypt_collaborator = await getCollaboratorEdit(page)
    # Se nao possuir usuario autenticado
    if encrypt_collaborator is None:
        return None
    stored_collaborator = decryptedUser(encrypt_collaborator)
    return stored_collaborator

async def setCategoryEdit(page: ft.Page, service):
    await page.client_storage.set_async(f"category{FLET_PATH}", service)

async def getCategoryEdit(page: ft.Page):
    return await page.client_storage.get_async(f"category{FLET_PATH}")

async def removeCategoryEdit(page: ft.Page):
    category = await getCategoryEdit(page)
    if category is not None:
        await page.client_storage.remove_async(f"category{FLET_PATH}")

async def loadCategoryEdit(page:ft.page):
    encrypt_category = await getCategoryEdit(page)
    # Se nao possuir usuario autenticado
    if encrypt_category is None:
        return None
    stored_category = decryptedUser(encrypt_category)
    return stored_category

async def setExpenseEdit(page: ft.Page, service):
    await page.client_storage.set_async(f"expense{FLET_PATH}", service)

async def getExpenseEdit(page: ft.Page):
    return await page.client_storage.get_async(f"expense{FLET_PATH}")

async def removeExpenseEdit(page: ft.Page):
    expense = await getExpenseEdit(page)
    if expense is not None:
        await page.client_storage.remove_async(f"expense{FLET_PATH}")

async def loadCategoryEdit(page:ft.page):
    encrypt_expense = await getExpenseEdit(page)
    # Se nao possuir usuario autenticado
    if encrypt_expense is None:
        return None
    stored_expense = decryptedUser(encrypt_expense)
    return stored_expense