from datetime import datetime
import time
import telegram

class TelegramModel():
    
    def __init__(self):
        self.chat_token = "1974464956:AAEvAvjGWwkjKgBVGB7sCUpDCAANtMS-yDo"
        self.bot = telegram.Bot(token = self.chat_token)
        self.user_lst = ['1339532440'] #나
    
    def get_userupdate(self):
        updates = self.bot.getUpdates()
        user_set = set()
        for u in updates:
            user_set.add(u.message['chat']['id'])
            self.user_lst = list(user_set)

    def send_message(self,text):
        self.get_userupdate()
        for usr in self.user_lst:
            self.bot.sendMessage(chat_id = usr, text=text)



