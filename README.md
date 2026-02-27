# tg-media-downloader

Telegram-бот для скачивания медиа из YouTube и Instagram.

## Возможности

- Скачивание видео/аудио из YouTube
- Скачивание медиа из Instagram (post/reel и т.д.)
- Ограничение размера отправляемых файлов (`MAX_FILE_SIZE`)
- Деплой через GitHub Actions + GHCR + Coolify

## Стек

- Python 3.11
- aiogram 3
- yt-dlp
- Docker / Docker Compose

## Структура проекта

```text
bot/
  handlers/
  services/
  utils/
  config.py
  main.py
Dockerfile
docker-compose.yml
docker-compose.yaml
requirements.txt
```

## Переменные окружения

Минимально необходимые:

- `BOT_TOKEN` - токен Telegram-бота от `@BotFather`
- `MAX_FILE_SIZE` - лимит размера файла в байтах (по умолчанию `52428800`)

Дополнительно (для антибот-защиты YouTube/Instagram):

- `YTDLP_COOKIEFILE` - путь до `cookies.txt` (например `/app/downloads/cookies.txt`)
- `INSTAGRAM_USERNAME` - логин Instagram (опционально)
- `INSTAGRAM_PASSWORD` - пароль Instagram (опционально)

Для VPN/прокси-туннеля (если сервер в РФ и нужны заблокированные ресурсы):

- `PROXY_URL=http://<proxy-host>:<proxy-port>`
- `HTTP_PROXY=${PROXY_URL}`
- `HTTPS_PROXY=${PROXY_URL}`
- `http_proxy=${PROXY_URL}`
- `https_proxy=${PROXY_URL}`
- `ALL_PROXY=${PROXY_URL}`
- `NO_PROXY=localhost,127.0.0.1`

## Локальный запуск

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Создать `.env` на основе `.env.example` и заполнить `BOT_TOKEN`.

3. Запустить:

```bash
python -m bot.main
```

## Запуск через Docker

Сборка:

```bash
docker build -t tg-media-downloader .
```

Запуск:

```bash
docker compose up -d
```

## Деплой (GitHub + Coolify)

Рекомендуемая схема:

1. Push в `main`
2. GitHub Actions собирает и пушит образ в GHCR
3. Coolify тянет готовый образ и запускает контейнер

Если в Coolify нет Build Pack `Docker Image`, используй `Docker Compose` и путь `/docker-compose.yaml`.

## Важные замечания

1. Не храните реальные токены и cookies в git.
2. YouTube/Instagram могут требовать авторизацию (cookies) на сервере, даже если локально все работает без нее.
3. Для доступа к заблокированным ресурсам должен быть настроен рабочий приватный VPN/прокси-туннель (`PROXY_URL`) без публикации endpoint в репозитории.
