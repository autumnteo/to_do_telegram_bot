from database_helper import DBHelper
from bot import telegram_chatbot


db = DBHelper("todo.sqlite")
bot = telegram_chatbot("config.cfg")

def main():
    db.setup()
    update_id = None
    while True:
        updates = bot.get_updates(offset=update_id)
        updates = updates["result"]
        if updates:
            for item in updates:
                update_id = item["update_id"]
                try:
                    message = str(item["message"]["text"])
                except:
                    message = None
                chat_id= item["message"]["chat"]["id"]
                bot.handle_updates(db, message, chat_id)


if __name__ == '__main__':
    main()