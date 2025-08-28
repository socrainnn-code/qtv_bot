import tweepy
import gspread
from google.oauth2 import service_account
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('QTVBot')

class QTVBot:
    def __init__(self):
        self.twitter_client = None
        self.sheet = None
        
    def initialize_twitter(self):
        """Инициализация Twitter клиента"""
        try:
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if not bearer_token:
                raise ValueError("TWITTER_BEARER_TOKEN not set")
                
            self.twitter_client = tweepy.Client(bearer_token=bearer_token)
            logger.info("✅ Twitter client initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Twitter: {e}")
            return False
    
    def initialize_google_sheets(self):
        """Инициализация Google Sheets"""
        try:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found")
                
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            gc = gspread.authorize(credentials)
            
            spreadsheet_id = os.getenv('SPREADSHEET_ID')
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID not set")
                
            spreadsheet = gc.open_by_key(spreadsheet_id)
            self.sheet = spreadsheet.sheet1
            
            logger.info("✅ Google Sheets initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets: {e}")
            return False
    
    def get_likes_count(self):
        """Получение количества лайков"""
        try:
            tweet_id = os.getenv('TARGET_TWEET_ID')
            if not tweet_id:
                raise ValueError("TARGET_TWEET_ID not set")
                
            tweet = self.twitter_client.get_tweet(tweet_id, tweet_fields=['public_metrics'])
            
            if tweet and tweet.data:
                likes = tweet.data.public_metrics.get('like_count', 0)
                logger.info(f"❤️ Current likes: {likes}")
                return likes
            else:
                logger.warning("⚠️ No tweet data received")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Failed to get likes: {e}")
            return None
    
    def update_sheets(self, likes_count):
        """Обновление Google Sheets"""
        try:
            current_time = str(datetime.now())
            self.sheet.update('A2', [[likes_count]])
            self.sheet.update('B2', [[current_time]])
            logger.info(f"📊 Updated sheets with {likes_count} likes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update sheets: {e}")
            return False
    
    def run(self):
        """Основной метод запуска"""
        logger.info("🚀 Starting QTV Bot")
        
        if not self.initialize_twitter():
            return False
            
        if not self.initialize_google_sheets():
            return False
            
        likes_count = self.get_likes_count()
        if likes_count is None:
            return False
            
        if not self.update_sheets(likes_count):
            return False
            
        logger.info("✅ QTV Bot completed successfully")
        return True

def main():
    bot = QTVBot()
    success = bot.run()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
