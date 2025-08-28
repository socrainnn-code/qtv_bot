import tweepy
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
import os
import logging
import json
import jwt  # Добавляем для проверки JWT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('QTVBot')

def validate_jwt_token(private_key, client_email):
    """Проверяет валидность JWT токена"""
    try:
        # Пробуем создать JWT токен
        now = datetime.utcnow()
        payload = {
            'iss': client_email,
            'scope': 'https://www.googleapis.com/auth/spreadsheets',
            'aud': 'https://oauth2.googleapis.com/token',
            'exp': now + timedelta(hours=1),
            'iat': now
        }
        
        # Пробуем подписать токен
        signed_jwt = jwt.encode(payload, private_key, algorithm='RS256')
        logger.info("✅ JWT token validation successful")
        return True
        
    except jwt.InvalidKeyError as e:
        logger.error(f"❌ Invalid private key: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ JWT validation error: {e}")
        return False

def check_credentials_file():
    """Проверяет credentials.json перед использованием"""
    try:
        if not os.path.exists('credentials.json'):
            logger.error("❌ credentials.json file not found")
            return False
        
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Проверяем обязательные поля
        required_fields = ['type', 'project_id', 'private_key', 'client_email', 'private_key_id']
        for field in required_fields:
            if field not in creds_data:
                logger.error(f"❌ Missing field in credentials: {field}")
                return False
        
        # Проверяем что private_key имеет правильный формат
        private_key = creds_data['private_key']
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            logger.error("❌ Private key has invalid format")
            return False
        
        # Валидируем JWT токен
        if not validate_jwt_token(private_key, creds_data['client_email']):
            return False
        
        logger.info(f"✅ credentials.json valid for: {creds_data['client_email']}")
        return True
        
    except json.JSONDecodeError:
        logger.error("❌ credentials.json contains invalid JSON")
        return False
    except Exception as e:
        logger.error(f"❌ Error validating credentials: {e}")
        return False

def initialize_google_sheets():
    """Инициализация Google Sheets с улучшенной обработкой ошибок"""
    if not check_credentials_file():
        return None
    
    try:
        # Загружаем credentials
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Создаем клиент с таймаутами
        gc = gspread.Client(credentials)
        gc.session.timeout = 30
        
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            logger.error("❌ SPREADSHEET_ID not set")
            return None
        
        # Пробуем открыть таблицу
        spreadsheet = gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.sheet1
        
        # Тестируем соединение простым запросом
        sheet.get('A1')
        
        logger.info("✅ Google Sheets initialized successfully")
        return sheet
        
    except gspread.SpreadsheetNotFound:
        logger.error("❌ Spreadsheet not found. Check SPREADSHEET_ID and sharing permissions")
        return None
    except gspread.NoValidUrlKeyFound:
        logger.error("❌ Invalid spreadsheet ID format")
        return None
    except gspread.APIError as e:
        logger.error(f"❌ Google API error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Google Sheets: {e}")
        return None

def main():
    logger.info("🚀 Starting QTV Bot")
    
    # Проверяем переменные окружения
    required_env_vars = ['TWITTER_BEARER_TOKEN', 'SPREADSHEET_ID', 'TARGET_TWEET_ID']
    for var in required_env_vars:
        if not os.getenv(var):
            logger.error(f"❌ Missing environment variable: {var}")
            return
    
    # Инициализируем Google Sheets
    sheet = initialize_google_sheets()
    if not sheet:
        logger.error("❌ Failed to initialize Google Sheets. Check credentials and spreadsheet sharing.")
        return
    
    # Остальная логика бота...
