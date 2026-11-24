"""Минимальный тест: пускает ли Telegram бота с хостинга BotHost.

Токен берётся из переменной окружения BOT_TOKEN (поле Bot Token в BotHost).
Раз в минуту пробует getMe. Как только получилось, отвечает на любое сообщение
«Работаю, проверка пройдена» и печатает id чата (для /chatid).
"""
import json
import os
import time
import urllib.error
import urllib.request

TOKEN = (os.environ.get("BOT_TOKEN") or os.environ.get("TOKEN") or "").strip()
API = "https://api.telegram.org/bot%s/" % TOKEN


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def call(method, **params):
    req = urllib.request.Request(API + method, data=json.dumps(params).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=80) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


def main():
    if not TOKEN:
        log("Нет BOT_TOKEN")
        return
    while True:
        try:
            r = call("getMe")
        except Exception as e:
            log("getMe: ошибка сети", type(e).__name__)
            time.sleep(60)
            continue
        if r.get("ok"):
            log("УСПЕХ: Telegram пустил бота @%s" % r["result"].get("username"))
            break
        log("getMe:", r.get("error_code"), r.get("description"))
        time.sleep(60)
    offset = 0
    while True:
        try:
            r = call("getUpdates", offset=offset, timeout=50)
        except Exception as e:
            log("getUpdates: ошибка сети", type(e).__name__)
            time.sleep(5)
            continue
        for u in r.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message")
            if msg:
                chat = msg["chat"]["id"]
                log("сообщение из чата", chat)
                call("sendMessage", chat_id=chat,
                     text="Работаю, проверка пройдена. Id этого чата: %s" % chat)


if __name__ == "__main__":
    main()
