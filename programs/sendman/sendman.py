class chatIds:
    felipe = "CHAT ID"
    ana = "CHAT ID"


def send(id, message, botInstance):
    botInstance.sendMessage(chat_id=id, text=message)
