from chatbot import Chatbot
from botapi.User import get_user


if __name__ == "__main__":
    user_data = get_user()
    if user_data:
        chatbot = Chatbot(user_data)
    else:
        chatbot = Chatbot(None)

    chatbot.start()

