import tweepy
import gspread
from google.oauth2 import service_account
import time
from datetime import datetime
import os
import logging

# Настройка логирования для GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self):
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Инициализация Twitter клиента с приоритетом Bearer Token"""
        try:
            # Пробуем Bearer Token сначала
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token and bearer_token != 'your_bearer_token_here':
                client = tweepy.Client(bearer_token=bearer_token)
                logger.info("✅ Twitter client initialized with Bearer Token")
                return client
            
            # Fallback на OAuth 1.0a
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_secret = os.getenv('TWITTER_ACCESS_SECRET')
            
            if all([api_key, api_secret, access_token, access_secret]):
                client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_secret
                )
                logger.info("✅ Twitter client initialized with OAuth 1.0a")
                return client
            
            logger.error("❌ No Twitter credentials found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Twitter client init error: {e}")
            return None

class GoogleSheetsClient:
    def __init__(self):
        self.sheet = self._initialize_sheets()
    
    def _initialize_sheets(self):
        """Инициализация Google Sheets"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json', 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            gc = gspread.authorize(credentials)
            spreadsheet_id = os.getenv('SPREADSHEET_ID')
            spreadsheet = gc.open_by_key(spreadsheet_id)
            return spreadsheet.sheet1
            
        except Exception as e:
            logger.error(f"❌ Google Sheets init error: {e}")
            return None

def main():
    logger.info("🚀 Starting QTV Bot on GitHub Actions")
    
    # Инициализация клиентов
    twitter_client = TwitterClient()
    sheets_client = GoogleSheetsClient()
    
    if not twitter_client.client or not sheets_client.sheet:
        logger.error("❌ Failed to initialize clients")
        return
    
    # Получаем лайки
    tweet_id = os.getenv('TARGET_TWEET_ID')
    like_count = twitter_client.client.get_tweet_likes(tweet_id)
    
    if like_count is not None:
        logger.info(f"❤️ Current likes: {like_count}")
        
        # Здесь ваша логика обновления Google Sheets
        # ...
        
    else:
        logger.error("❌ Failed to get likes")

if __name__ == "__main__":
    main()
