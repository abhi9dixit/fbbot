import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request


####

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os
bot= ChatBot("Bot")
bot.set_trainer(ListTrainer)
for files in os.listdir('zchatbot/chatterbot-corpus-master/chatterbot_corpus/data/english/'):
    data = open('zchatbot/chatterbot-corpus-master/chatterbot_corpus/data/english/' + files, 'r').readlines()
    bot.train(data)

# while True:
#     message = input('You :')
#     if message.strip() != 'Bye':
#         reply = bot.get_response(message)
#         print ('ChatBot :', reply)
#     if message.strip() == 'Bye':
#         print('ChatBot : Bye')
#         break


def myChatBot(query):
    if query.strip() == 'Bye':
        return 'Bye'
    return bot.get_response(query.strip())

####

app = Flask(__name__)




@app.route('/', methods=['GET'])
def verify():
    # endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():


    data = request.get_json()
    log(data)  

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        
                    recipient_id = messaging_event["recipient"]["id"]  
                    message_text = messaging_event["message"]["text"]  

                    send_message(sender_id, "hello how may i help you")

                ######

                if message_text:
                    botReply = myChatBot(message_text)
                    if not botReply:
                        botReply = "Sorry! Could not understand you message :)"
                    send_message(sender_id, botReply)

                ######

                # if messaging_event.get("delivery"):  
                #     pass

                # if messaging_event.get("optin"):  
                #     pass

                # if messaging_event.get("postback"):  
                #     pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(port=8080,debug=True)
