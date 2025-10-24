import os
import subprocess
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import time

# Токены берём из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")  # Введите логин GitHub
SSH_USER = os.getenv("SSH_USER")         # SSH юзер (обычно логин GitHub)

CODESPACE_REPO = os.getenv("CODESPACE_REPO", "v-starshinin/blackpearl")

COD_SERVER_PORT = 1080

# Получить список codespace
def list_codespaces(update: Update, context: CallbackContext):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    url = "https://api.github.com/user/codespaces"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        codespaces = r.json().get("codespaces", [])
        if codespaces:
            msg = "Ваши Codespaces:\n"
            for idx, c in enumerate(codespaces, 1):
                msg += f'{idx}. {c["name"]} ({c["state"]}): {c["web_url"]}\n'
            update.message.reply_text(msg)
        else:
            update.message.reply_text("Нет активных codespaces.")
    else:
        update.message.reply_text(f"Ошибка доступа к GitHub API: {r.status_code}")

# Запустить codespace (repo задаётся env либо хардкодом)
def create_codespace(update: Update, context: CallbackContext):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/user/codespaces"
    data = {"repository": CODESPACE_REPO, "machine": "basicLinux"}
    # Optional: branch, location и т.д. можно указать
    r = requests.post(url, headers=headers, json=data)
    if r.status_code in (200, 201):
        cs = r.json()
        msg = f"Codespace {cs['name']} создается. Ждите..."
        update.message.reply_text(msg)
    else:
        update.message.reply_text(f"Ошибка создания codespace: {r.status_code} {r.text}")

# Получить ssh host codespace по имени
def get_codespace_host(codespace_name):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    url = f"https://api.github.com/user/codespaces/{codespace_name}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("connection", {}).get("ssh", {}).get("host")
    return None

# Команда для старта туннеля автоматически (бот на домашней машине)
def tunnel(update: Update, context: CallbackContext):
    # Узнаём список codespace
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    r = requests.get("https://api.github.com/user/codespaces", headers=headers)
    codespaces = r.json().get("codespaces", [])
    if not codespaces:
        update.message.reply_text("Нет активных codespaces! Запустите сначала codespace.")
        return
    cs = codespaces[0]  # Для простоты берём первый активный
    name = cs["name"]
    ssh_host = cs["connection"]["ssh"]["host"]
    ssh_user = cs["connection"]["ssh"]["user"]
    # Можно запускать несколькими способами:
    # Команда для копипаста:
    ssh_cmd = f"ssh -N -L {COD_SERVER_PORT}:localhost:{COD_SERVER_PORT} {ssh_user}@{ssh_host}"
    update.message.reply_text(f"Для туннеля выполните локально: {ssh_cmd}")
    # Или (автоматически), если бот на вашей машине:
    try:
        subprocess.Popen(["ssh", "-N", "-L", f"{COD_SERVER_PORT}:localhost:{COD_SERVER_PORT}", f"{ssh_user}@{ssh_host}"])
        update.message.reply_text(f"Туннель открыт! SOCKS5 будет доступен на 127.0.0.1:{COD_SERVER_PORT}")
    except Exception as e:
        update.message.reply_text(f"Ошибка при открытии туннеля: {str(e)}")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет!\n/codespaces — показать список\n/create — создать codespace\n/tunnel — открыть SSH-туннель к первому активному codespace.")

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("codespaces", list_codespaces))
    dp.add_handler(CommandHandler("create", create_codespace))
    dp.add_handler(CommandHandler("tunnel", tunnel))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
