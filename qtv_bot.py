import tweepy
import gspread
from google.oauth2 import service_account
from datetime import datetime
import os
import logging
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('QTVBot')

def get_tweet_likes(client, tweet_id):
    """Правильное получение количества лайков твита"""
    try:
        tweet = client.get_tweet(tweet_id, tweet_fields=['public_metrics'])
        if tweet and tweet.data:
            return tweet.data.public_metrics.get('like_count', 0)
        return 0
    except Exception as e:
        logger.error(f"❌ Error getting tweet likes: {e}")
        return None

def initialize_google_sheets():
    """Инициализация Google Sheets"""
    try:
        if not os.path.exists('credentials.json'):
            logger.error("❌ credentials.json file not found")
            return None
        
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        gc = gspread.authorize(credentials)
        
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            logger.error("❌ SPREADSHEET_ID environment variable not set")
            return None
        
        spreadsheet = gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.sheet1
        
        logger.info("✅ Google Sheets initialized successfully")
        return sheet
        
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
        logger.error("❌ Failed to initialize Google Sheets")
        return
    
    # Инициализируем Twitter клиент
    try:
        client = tweepy.Client(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))
        logger.info("✅ Twitter client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Twitter client: {e}")
        return
    
    # Получаем количество лайков ПРАВИЛЬНЫМ методом
    tweet_id = os.getenv('TARGET_TWEET_ID')
    like_count = get_tweet_likes(client, tweet_id)
    
    if like_count is None:
        logger.error("❌ Failed to get tweet likes")
        return
    
    logger.info(f"❤️ Current likes: {like_count}")
    
    # Обновляем Google Sheets
    try:
        current_time = str(datetime.now())
        sheet.update('A2', [[like_count]])
        sheet.update('B2', [[current_time]])
        
        logger.info(f"📊 Updated Google Sheets with {like_count} likes")
        
    except Exception as e:
        logger.error(f"❌ Failed to update Google Sheets: {e}")
        return
    
    logger.info("✅ QTV Bot completed successfully")

if __name__ == "__main__":
    main()
