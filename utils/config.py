from dotenv import load_dotenv
import os

load_dotenv()

COLOR_BACKGROUND_PAGE = os.getenv("COLOR_BACKGROUND_PAGE")        # Fundo da página, rosa claro
COLOR_BACKGROUND_CONTAINER = os.getenv("COLOR_BACKGROUND_CONTAINER")   # Contêineres, branco
COLOR_BACKGROUND_BUTTON = os.getenv("COLOR_BACKGROUND_BUTTON")      # Botões, rosa suave
COLOR_BACKGROUND_TEXT_FIELD = os.getenv("COLOR_BACKGROUND_TEXT_FIELD")  # Campos de texto, branco
COLOR_TEXT_BUTTON = os.getenv("COLOR_TEXT_BUTTON")            # Texto dos botões, branco
COLOR_TEXT = os.getenv("COLOR_TEXT")                  # Texto estático, cinza escuro
COLOR_TEXT_IN_BUTTON = os.getenv("COLOR_TEXT_IN_BUTTON")         # Texto dentro dos botões, rosa vibrante
COLOR_TEXT_IN_DROPDOWN = os.getenv("COLOR_TEXT_IN_DROPDOWN") 
COLOR_TEXT_IN_FIELD = os.getenv("COLOR_TEXT_IN_FIELD")         # Texto nos campos de entrada, cinza escuro
COLOR_BORDER_COLOR = os.getenv("COLOR_BORDER_COLOR")           # Cor das bordas, rosa vibrante
COLOR_BORDER_COLOR_ERROR = os.getenv("COLOR_BORDER_COLOR_ERROR")     # Cor das bordas de erro, vermelho
URL_MAPS = os.getenv("URL_MAPS")  # URL para os mapas
SECRET_KEY = os.getenv("MY_APP_SECRET_KEY")
FLET_PATH = os.getenv("FLET_PATH")
IMG_LOGO = "icon.png"

# API_URL = "http://api-cache-firestore:8000"
API_URL = "http://localhost:8000"