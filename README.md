# QTV Twitter Bot 🤖

Автоматический бот для отслеживания лайков твита и обновления Google Sheets.

## 🚀 Как работает

1. Каждые 5 минут проверяет количество лайков указанного твита
2. Обновляет данные в Google Sheets
3. Работает полностью автоматически в облаке GitHub

## ⚙️ Настройка

### Secrets в GitHub:

- `TWITTER_BEARER_TOKEN` - Twitter API Bearer Token
- `SPREADSHEET_ID` - ID Google таблицы
- `TARGET_TWEET_ID` - ID отслеживаемого твита
- `GOOGLE_CREDENTIALS` - содержимое credentials.json

### Google Sheets структура:

| A | B | C |
|---|---|---|
| Текущие лайки | Время обновления | Статус |

## 📊 Мониторинг

- Логи: Actions → QTV Twitter Bot → конкретный run
- Статус: Вкладка Actions репозитория
- Данные: Ваша Google таблица

## 🔧 Локальная разработка

```bash
pip install -r requirements.txt
python qtv_bot.py
