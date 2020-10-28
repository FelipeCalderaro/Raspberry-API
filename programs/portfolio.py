import requests
import json


def sendMessage(name, email, text, bot):
    message = f"PORTFOLIO\n\nNome do remetente: {name}\nEmail do remetente: {email}\n\n{text}"
    bot.sendMessage(chat_id=277634087, text=message)
    return {"status": 200}
