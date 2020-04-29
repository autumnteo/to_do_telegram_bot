import requests
import json
import configparser as cfg

class telegram_chatbot():

    def __init__(self, config):
        self.token = self.read_token_from_config_file(config)
        self.base = "https://api.telegram.org/bot{}/".format(self.token)

    def read_token_from_config_file(self, config):
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds', 'token')

    def get_updates(self, offset=None):
        url = self.base + "getUpdates?timeout=100"
        if offset:
            url = url + "&offset={}".format(offset + 1)
        r = requests.get(url)
        return json.loads(r.content)

    def send_message(self, msg, chat_id, reply_markup=None):
        url = self.base + "sendMessage?chat_id={}&text={}".format(chat_id, msg)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
        if msg is not None:
            requests.get(url)

    def build_keyboard(self, items):
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def handle_updates(self, db, text, chat):
        items = db.get_items(chat)
        if text == "/delete":
            keyboard = self.build_keyboard(items)
            self.send_message("Select an item to delete", chat, keyboard)
        elif text == "/start":
            self.send_message("Welcome to your personal To Do list. Send any text to me and I'll store it as an item. Send /delete to remove items", chat)
        elif text.startswith("/"):
            self.send_message("The only commands i understand are /start and /delete", chat)
        elif text in items:
            db.delete_item(text, chat)
            items.remove(text)
            if len (items) == 0:
                self.send_message("You current To Do List is empty.\nPlease enter any text to store it as an item", chat)
            else:
                keyboard = self.build_keyboard(items)
                self.send_message("Select an item to delete", chat, keyboard)
        else:
            db.add_item(text, chat)
            items.append(text)
            items = [item.title() for item in items]
            new_item_list = [f'{index}. {elm}' for index, elm in enumerate(items, start=1)]
            message = "The current items in your To Do List are:\n"
            message += "\n".join(new_item_list)
            self.send_message(message, chat)