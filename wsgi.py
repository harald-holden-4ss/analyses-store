from dotenv import load_dotenv
load_dotenv()
from app.fast_api_app import get_app
app = get_app()
