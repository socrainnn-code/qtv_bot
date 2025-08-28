import tweepy
import gspread
from google.oauth2 import service_account
from datetime import datetime
import os
import logging
import time
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('QTVBot')

# Контрольные точки для ответных твитов
MILESTONES = [100, 500, 1000, 5000, 10000, 25000, 50000, 75000, 100000]
TARGET_GOAL = 100000

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

def update_google_sheets(sheet, likes_count, last_checkpoint, status="Active"):
    """Обновление Google Sheets с отслеживанием контрольных точек"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Обновляем данные
        update_data = [
            [likes_count],          # A2 - Текущие лайки
            [last_checkpoint],      # B2 - Последняя контрольная точка
            [TARGET_GOAL],          # C2 - Целевое значение
            [current_time],         # D2 - Время обновления
            [status]                # E2 - Статус
        ]
        
        sheet.update('A2:E2', update_data)
        logger.info(f"📈 Updated Google Sheets: {likes_count} likes")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update Google Sheets: {e}")
        return False

def post_milestone_tweet(client, tweet_id, current_likes, milestone):
    """Публикация ответного твита при достижении контрольной точки"""
    try:
        # Выбираем сообщение в зависимости от milestone
        if milestone == 100:
            message = f"🎉 Первые 100 лайков! Спасибо за доверие к эксперименту! 🙏\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 500:
            message = f"🔥 500 лайков! Сообщество растет не по дням, а по часам! 🌱\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 1000:
            message = f"⚡ 1000 лайков! Алгоритмы Twitter начали нас замечать! 📊\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 5000:
            message = f"🌟 5000 лайков! Мы на полпути к разгадке тайны! 🎯\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 10000:
            message = f"💫 10,000 лайков! Сила коллективного разума впечатляет! 🧠\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 25000:
            message = f"🚀 25,000 лайков! Виральный эффект набирает обороты! 🌪️\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 50000:
            message = f"🎯 50,000 лайков! Половина пути пройдена блестяще! ✨\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 75000:
            message = f"🔥 75,000 лайков! Финал уже близко, осталось совсем немного! ⏳\n\nТекущий прогресс: {current_likes}/{TARGET_GOAL} 👁️⚡️\n#QTV #QuestToVision"
        elif milestone == 100000:
            message = f"🏆 100,000 ЛАЙКОВ ДОСТИГНУТО! Тайна раскрыта! 🎊\n\nСпасибо каждому, кто участвовал в этом путешествии! 🙌\n#QTV #QuestToVision #Победа"
        else:
            progress_percent = (current_likes / TARGET_GOAL) * 100
            message = f"🚀 Прогресс: {current_likes}/{TARGET_GOAL} ({progress_percent:.1f}%)\n\nДостигнута новая веха! Продолжаем в том же духе! 👁️⚡️\n#QTV #QuestToVision"
        
        # Публикуем твит как ответ на основной твит
        response = client.create_tweet(
            text=message,
            in_reply_to_tweet_id=tweet_id
        )
        
        logger.info(f"📢 Published milestone tweet: {milestone} likes")
        logger.info(f"   Tweet ID: {response.data['id']}")
        return True
        
    except tweepy.TooManyRequests as e:
        logger.warning(f"⏳ Rate limit for tweeting: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to post milestone tweet: {e}")
        return False

def check_milestones(client, tweet_id, current_likes, last_checkpoint):
    """Проверяет достижение контрольных точек и публикует твиты"""
    new_checkpoint = last_checkpoint
    
    for milestone in MILESTONES:
        if current_likes >= milestone > last_checkpoint:
            logger.info(f"🎯 Milestone reached: {milestone} likes!")
            
            # Публикуем ответный твит
            if post_milestone_tweet(client, tweet_id, current_likes, milestone):
                new_checkpoint = milestone
                logger.info(f"✅ Milestone {milestone} celebrated with tweet")
            else:
                logger.warning(f"⚠️ Failed to tweet for milestone {milestone}")
    
    return new_checkpoint

def load_last_checkpoint(sheet):
    """Загружает последнюю контрольную точку из Google Sheets"""
    try:
        # Читаем значение из ячейки B2
        checkpoint_value = sheet.acell('B2').value
        if checkpoint_value and checkpoint_value.isdigit():
            return int(checkpoint_value)
        return 0
    except Exception as e:
        logger.warning(f"⚠️ Could not load last checkpoint: {e}")
        return 0

def main():
    logger.info("=" * 50)
    logger.info("🚀 STARTING QTV BOT WITH MILESTONES")
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
    
    # Загружаем последнюю контрольную точку
    last_checkpoint = load_last_checkpoint(sheet)
    logger.info(f"📊 Last checkpoint: {last_checkpoint}")
    
    # Получаем количество лайков
    tweet_id = os.getenv('TARGET_TWEET_ID')
    logger.info(f"📨 Fetching likes for tweet: {tweet_id}")
    
    like_count = get_tweet_likes(client, tweet_id)
    
    if like_count is None:
        logger.error("❌ Failed to get tweet likes")
        return False
    
    # Проверяем и отмечаем контрольные точки
    new_checkpoint = check_milestones(client, tweet_id, like_count, last_checkpoint)
    
    # Определяем статус
    status = "Completed" if like_count >= TARGET_GOAL else "Active"
    
    # Обновляем Google Sheets
    if not update_google_sheets(sheet, like_count, new_checkpoint, status):
        logger.error("❌ Failed to update Google Sheets")
        return False
    
    # Если достигли цели - особое сообщение
    if like_count >= TARGET_GOAL and last_checkpoint < TARGET_GOAL:
        logger.info("🏆 TARGET GOAL ACHIEVED! Mission accomplished!")
    
    logger.info("=" * 50)
    logger.info(f"🎉 QTV BOT COMPLETED! Current: {like_count}, Checkpoint: {new_checkpoint}")
    logger.info("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
