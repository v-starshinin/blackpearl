# Blackpearl — Codespace SOCKS5 + Telegram Bot Proxy

## TL;DR
- Поднимает SOCKS5 сервер внутри GitHub Codespace
- Управляется через Telegram-бота
- Автоматически создаёт ssh-туннель с домашней машины

---

## Быстрый старт

### 1. Установить зависимости
```
pip install -r requirements.txt
```

### 2. Запуск SOCKS5 сервера в Codespace
```
python3 socks5_server.py
```

### 3. Настройте переменные окружения на домашней машине
- `TELEGRAM_TOKEN` — Токен вашего телеграм-бота
- `GITHUB_TOKEN` — Github personal access token с правами Codespaces
- `GITHUB_USER` — ваш GitHub username
- `SSH_USER` — ваш ssh username (чаще совпадает с GitHub)
- (опционально) `CODESPACE_REPO` — "v-starshinin/blackpearl" для примера

### 4. Запуск Telegram-бота на домашней машине
```
python3 telegram_bot.py
```

---

## Как это работает

1. Через Telegram выбираете:
	- `/codespaces` — список Codespaces
	- `/create` — создать Codespace для proxy (socks5_server автоматом стартует)
	- `/tunnel` — бот предложит команду ssh-туннеля или автоматически поднимет его (если бот запущен на вашей машине)
2. SOCKS5 сразу доступен: 127.0.0.1:1080

---

## Ссылки
- [GitHub Codespaces API Docs](https://docs.github.com/en/rest/codespaces?apiVersion=2022-11-28)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [PySocks](https://github.com/Anorov/PySocks)