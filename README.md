# 📬 Предложка Telegram Bot / Suggestion Bot

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://core.telegram.org/bots)

**RU:** Асинхронный Telegram-бот для сбора предложений и обратной связи от пользователей. Идеально подходит для каналов, сообществ и бизнеса.

**EN:** Async Telegram bot for collecting suggestions and feedback. Perfect for channels, communities and businesses.

## ✨ Возможности

- 📨 **Приём контента** — текст, фото, видео, голосовые, кружочки, документы, геолокация, контакты, альбомы
- 👥 **Модерация** — заявки попадают в закрытую админ-группу с кнопками управления
- 🚫 **Анти-спам** — троттлинг (1 сообщение в 3 сек) и бан спамеров
- 📢 **Рассылка** — массовая отправка сообщений всем пользователям
- ↩️ **Ответы** — возможность ответить пользователю от имени бота
- 📊 **Статистика** — отчёты по рассылкам

## 🛠 Технологии

- **Python 3.11+**
- **aiogram 3.x** — асинхронный фреймворк для Telegram Bot API
- **aiosqlite** — асинхронная работа с SQLite
- **python-dotenv** — управление конфигурацией

## 📁 Структура проекта

```
predlo-bot/
├── src/
│   ├── handlers/       # Обработчики команд и сообщений
│   ├── keyboards/      # Inline-клавиатуры
│   ├── middlewares/    # Throttling, ban-check, album
│   ├── database/       # Модели и запросы к БД
│   ├── states/         # FSM состояния
│   ├── utils/          # Вспомогательные функции
│   ├── config.py       # Конфигурация
│   └── main.py         # Точка входа
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/zilbamo/telegram-suggestion-bot.git
cd telegram-suggestion-bot
```

### 2. Виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Конфигурация

```bash
cp .env.example .env
```

Отредактируй `.env`:

```env
BOT_TOKEN=123456:ABC-DEF...        # Токен от @BotFather
ADMIN_GROUP_ID=-1001234567890      # ID админ-группы
ADMIN_IDS=123456789,987654321      # ID админов (через запятую)
```

> 💡 Получить ID группы: добавь [@getmyid_bot](https://t.me/getmyid_bot) в группу

### 5. Запуск

```bash
python -m src.main
```

## 🖥 Деплой на сервер (Ubuntu/Debian)

### Systemd сервис

```bash
sudo nano /etc/systemd/system/predlo-bot.service
```

```ini
[Unit]
Description=Predlo Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/predlo-bot
ExecStart=/home/YOUR_USER/predlo-bot/venv/bin/python -m src.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Команды управления

```bash
sudo systemctl daemon-reload        # Перечитать конфиги
sudo systemctl enable predlo-bot    # Автозапуск
sudo systemctl start predlo-bot     # Запустить
sudo systemctl stop predlo-bot      # Остановить
sudo systemctl restart predlo-bot   # Перезапустить
sudo systemctl status predlo-bot    # Статус
journalctl -u predlo-bot -f         # Логи
```

## 📖 Использование

### Для пользователей
- `/start` — начать работу с ботом
- Отправь любой контент — он попадёт к админам

### Для админов (в админ-группе)
- **👁 Взял** — пометить заявку как обработанную
- **🗑 Удалить** — удалить заявку
- **🚫 БАН** — заблокировать пользователя
- **↩️ Ответить** — ответить пользователю

### Команды админов
- `/broadcast` — начать рассылку (только для ID из ADMIN_IDS)

## 📝 Лицензия

MIT License — используй свободно.

## 🤝 Contributing

Pull requests приветствуются! Для крупных изменений сначала открой issue.

---

⭐ Если проект полезен — поставь звезду!
