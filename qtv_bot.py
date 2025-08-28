import tweepy
import gspread
from google.oauth2 import service_account
from datetime import datetime
import os
import logging
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('QTVBot')

def get_tweet_likes(client, tweet_id):
    """
    Получает количество лайков твита используя ПРАВИЛЬНЫЙ метод Tweepy v2
    """
    try:
        # ПРАВИЛЬНЫЙ метод: get_tweet с tweet_fields
        response = client.get_tweet(
            tweet_id, 
            tweet_fields=['public_metrics', 'author_id', 'created_at']
        )
        
        if response and response.data:
            likes = response.data.public_metrics.get('like_count', 0)
            logger.info(f"✅ Successfully retrieved tweet data")
            logger.info(f"   Tweet ID: {response.data.id}")
            logger.info(f"   Author ID: {response.data.author_id}")
            logger.info(f"   Likes: {likes}")
            return likes
        else:
            logger.warning("⚠️ No data in API response")
            return 0
            
    except tweepy.TooManyRequests as e:
        logger.error(f"⏳ Rate limit exceeded: {e}")
        return None
    except tweepy.NotFound as e:
        logger.error(f"❌ Tweet not found: {e}")
        return None
    except tweepy.Unauthorized as e:
        logger.error(f"❌ Authentication failed: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error getting tweet: {e}")
        return None

def initialize_google_sheets():
    """Инициализация Google Sheets"""
    try:
        if not os.path.exists('credentials.json'):
            logger.error("❌ credentials.json file not found")
            return None
        
        # Читаем и проверяем credentials
        with open('credentials.json', 'r') as f:
            import json
            data = json.load(f)
            logger.info(f"✅ Loaded credentials for: {data.get('client_email', 'unknown')}")
        
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        gc = gspread.authorize(credentials)
        
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            logger.error("❌ SPREADSHEET_ID environment variable not set")
            return None
        
        logger.info(f"📊 Opening spreadsheet: {spreadsheet_id}")
        spreadsheet = gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.sheet1
        
        # Проверяем доступ чтением первой ячейки
        test_value = sheet.acell('A1').value
        logger.info(f"✅ Google Sheets access confirmed. A1 value: '{test_value}'")
        
        return sheet
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Google Sheets: {e}")
        return None

def update_google_sheets(sheet, likes_count):
    """Обновление Google Sheets"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Обновляем данные
        sheet.update('A2', [[likes_count]])
        sheet.update('B2', [[current_time]])
        sheet.update('C2', [['Success']])
        
        logger.info(f"📈 Updated Google Sheets: {likes_count} likes at {current_time}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update Google Sheets: {e}")
        return False

def main():
    logger.info("=" * 50)
    logger.info("🚀 STARTING QTV BOT")
    logger.info("=" * 50)
    
    # Проверяем переменные окружения
    required_env_vars = ['TWITTER_BEARER_TOKEN', 'SPREADSHEET_ID', 'TARGET_TWEET_ID']
    env_status = {}
    
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: SET")
            env_status[var] = True
        else:
            logger.error(f"❌ {var}: NOT SET")
            env_status[var] = False
    
    if not all(env_status.values()):
        logger.error("❌ Missing required environment variables")
        return False
    
    # Проверяем credentials
    if not os.path.exists('credentials.json'):
        logger.error("❌ credentials.json file not found")
        return False
    
    # Инициализируем Twitter клиент
    try:
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        client = tweepy.Client(bearer_token=bearer_token)
        logger.info("✅ Twitter client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Twitter client: {e}")
        return False
    
    # Инициализируем Google Sheets
    sheet = initialize_google_sheets()
    if not sheet:
        logger.error("❌ Failed to initialize Google Sheets")
        return False
    
    # Получаем количество лайков
    tweet_id = os.getenv('TARGET_TWEET_ID')
    logger.info(f"📨 Fetching likes for tweet: {tweet_id}")
    
    like_count = get_tweet_likes(client, tweet_id)
    
    if like_count is None:
        logger.error("❌ Failed to get tweet likes")
        return False
    
    # Обновляем Google Sheets
    if not update_google_sheets(sheet, like_count):
        logger.error("❌ Failed to update Google Sheets")
        return False
    
    logger.info("=" * 50)
    logger.info("🎉 QTV BOT COMPLETED SUCCESSFULLY!")
    logger.info("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
