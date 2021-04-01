from botapi.User import get_user
from chatbot import Chatbot

if __name__ == "__main__":
    print("Getting information on previous sessions..")
    user_data = get_user()
    if user_data:
        chatbot = Chatbot(**user_data)
    else:
        chatbot = Chatbot(None)

    chatbot.start()

