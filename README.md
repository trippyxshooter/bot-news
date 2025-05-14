# 🤖 AI News Bot

**AI News Bot** — це Telegram бот, який автоматично збирає, аналізує та публікує новини з різних джерел. Використовує штучний інтелект для категоризації та створення щоденних дайджестів.

## 📋 Функціонал

- **Автоматичний збір новин** з різних джерел
- **AI-аналіз** та категоризація новин
- **Щоденні дайджести** з найважливішими новинами
- **Миттєві сповіщення** про важливі новини
- **Адміністративна панель** зі статистикою та налаштуваннями

## 🛠 Технічний стек

- **Python 3.11**
- **Docker** для контейнеризації
- **Telegram Bot API** для взаємодії з користувачами
- **GitHub Actions** для CI/CD
- **Prometheus** для метрик
- **Sentry** для моніторингу помилок
- **LLM**: Gemini 1.5 Flash + OpenAI GPT-4

## 📁 Структура проєкту

```
ai-news-bot/
├── app/
│   ├── __init__.py
│   ├── bot.py          # Основний клас бота
│   ├── config.py       # Налаштування (Settings)
│   ├── metrics.py      # Метрики Prometheus
│   ├── news/
│   │   ├── __init__.py
│   │   ├── collector.py # Збір новин
│   │   └── analyzer.py  # AI-аналіз новин
│   └── utils/
│       ├── __init__.py
│       └── helpers.py   # Допоміжні функції
├── tests/
│   ├── __init__.py
│   └── test_bot.py     # Тести для бота
├── .env                # Змінні середовища (не включено в Git)
├── .flake8            # Конфігурація flake8
├── .github/
│   └── workflows/
│       └── main.yml    # CI/CD пайплайн
├── Dockerfile         # Конфігурація Docker
├── requirements.txt   # Залежності Python
└── README.md          # Документація
```

## 🚀 Встановлення

### Локальне встановлення

1. **Клонуй репозиторій:**
   ```bash
   git clone https://github.com/ТВІЙ_ЛОГІН/ai-news-bot.git
   cd ai-news-bot
   ```

2. **Створи віртуальне середовище:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # або
   venv\Scripts\activate  # Windows
   ```

3. **Встанови залежності:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Створи файл `.env` з налаштуваннями:**
   ```
   # Telegram
   TELEGRAM_TOKEN=твій_токен
   TELEGRAM_CHANNEL_ID=твій_канал
   ADMIN_IDS=твій_id
   
   # LLM API Keys
   OPENAI_API_KEY=твій_ключ
   GOOGLE_API_KEY=твій_ключ
   
   # Monitoring
   SENTRY_DSN=твій_dsn
   ENABLE_METRICS=true
   METRICS_PORT=9090
   ```

5. **Запусти бота:**
   ```bash
   python -m app.bot
   ```

### Запуск через Docker

1. **Збери Docker-образ:**
   ```bash
   docker build -t ai-news-bot .
   ```

2. **Запусти контейнер:**
   ```bash
   docker run -d \
     --name ai-news-bot \
     -p 9090:9090 \
     -v $(pwd)/data.db:/app/data.db \
     --env-file .env \
     ai-news-bot
   ```

### Деплой на сервер

1. **Створи systemd сервіс:**
   ```ini
   # /etc/systemd/system/ai-news-bot.service
   [Unit]
   Description=AI News Bot
   After=network.target
   
   [Service]
   Type=simple
   User=ai-news-bot
   WorkingDirectory=/opt/ai-news-bot
   Environment=PYTHONPATH=/opt/ai-news-bot
   ExecStart=/usr/local/bin/docker-compose up
   ExecStop=/usr/local/bin/docker-compose down
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Створи docker-compose.yml:**
   ```yaml
   version: '3'
   services:
     bot:
       image: ai-news-bot:latest
       ports:
         - "9090:9090"
       volumes:
         - ./data.db:/app/data.db
       env_file:
         - .env
       restart: unless-stopped
   ```

3. **Запусти сервіс:**
   ```bash
   sudo systemctl enable ai-news-bot
   sudo systemctl start ai-news-bot
   ```

## 📊 Моніторинг

### Prometheus метрики

- **/metrics** endpoint на порту 9090
- Основні метрики:
  - `news_processed_total` - кількість оброблених новин
  - `news_impact` - розподіл impact-оцінок
  - `llm_requests_total` - кількість запитів до LLM
  - `llm_cost_usd` - вартість використання LLM
  - `duplicate_rate` - відсоток дублікатів

### Sentry

- Автоматичний збір помилок
- Трейси запитів
- Профілювання

### Health check

- **/healthz** endpoint для перевірки стану сервісу
- Перевіряє:
  - Підключення до БД
  - Статус планировщика
  - Версію додатку

## 📝 Використання

### Команди для адмінів

- `/stats` — статистика новин
- `/digest now` — створити дайджест зараз
- `/toggle [функція]` — увімкнути/вимкнути функцію

### Автоматичні функції

- **Щоденний дайджест** — публікується о 20:00
- **Breaking news** — миттєві сповіщення про важливі новини

## 🧪 Тестирование

### Unit тесты
```bash
# Запуск всех unit-тестов
pytest tests/unit -v

# Запуск конкретного теста
pytest tests/unit/test_summarizer.py -v

# Запуск с покрытием кода
pytest tests/unit --cov=app --cov-report=term-missing
```

### Интеграционные тесты
```bash
# Запуск всех интеграционных тестов
pytest tests/integration -v

# Запуск с покрытием
pytest tests/integration --cov=app --cov-report=term-missing
```

### Load тесты
```bash
# Запуск Locust
locust -f tests/load/locustfile.py

# Запуск с определенным количеством пользователей
locust -f tests/load/locustfile.py --users 100 --spawn-rate 10 --host http://localhost:8000
```

### Проверка кода
```bash
# Линтинг
ruff check .

# Типизация
mypy app/

# Форматирование
ruff format .
```

### CI/CD Pipeline
Проект использует GitHub Actions для автоматического тестирования:
1. Запуск unit-тестов
2. Запуск интеграционных тестов
3. Проверка типов
4. Линтинг
5. Форматирование
6. Сборка Docker-образа
7. Деплой на тестовый сервер

### Масштабируемость
Проект спроектирован с учетом масштабирования:
1. Асинхронная обработка новостей
2. Поддержка нескольких LLM моделей
3. Метрики для мониторинга производительности
4. Docker-контейнеризация
5. Возможность горизонтального масштабирования

### Расширяемость
Архитектура позволяет легко добавлять новые функции:
1. Модульная структура кода
2. Поддержка новых источников новостей
3. Возможность добавления новых LLM моделей
4. Гибкая система метрик
5. Конфигурируемые параметры

## 🔄 CI/CD

Проєкт використовує GitHub Actions для:
- Автоматичного тестування
- Лінтування коду
- Збірки Docker-образу
- Деплою на сервер

## 📄 Ліцензія

MIT

## 👥 Автори

- Твоє ім'я — [GitHub](https://github.com/ТВІЙ_ЛОГІН)

---

**Приємного використання!** 🚀 