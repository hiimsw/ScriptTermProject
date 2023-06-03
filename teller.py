import sys
import traceback
import telepot

class Teller:
    def __init__(self):
        self.__bot = None

    def connect_api(self, key):
        self.__bot = telepot.Bot(key)

    def set_message_handler(self, message_handelr):
        assert self.__bot is not None, "api가 연결되지 않아 이 함수를 호출할 수 없습니다."
        self.__bot.message_loop(message_handelr)

    def send_message(self, user_id, msg):
        assert self.__bot is not None, "api가 연결되지 않아 이 함수를 호출할 수 없습니다."

        try:
            self.__bot.sendMessage(user_id, msg)
        except:
            traceback.print_exc(file=sys.stdout)

    def is_connected(self):
        return self.__bot is not None



