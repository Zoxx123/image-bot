import requests
import time
import os
import json
import sqlite3

TOKEN = ""
URL = f"https://api.telegram.org/bot{TOKEN}/"

CONNECT = sqlite3.connect('./lesson5/botdatabase.db')
CURSOR = CONNECT.cursor()

on_bot = True
get_description_img = [] 

def add_user(chat_id,name):
    CURSOR.execute(f'INSERT INTO Users (name, chatid) VALUES ("{name}",{chat_id})')
    CONNECT.commit()

def initial_db():
    CURSOR.execute('''
                CREATE TABLE IF NOT EXISTS Users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    chatid INTEGER
                )
    ''')


def user_check(chat_id,name):
    CURSOR.execute(f'SELECT * FROM Users WHERE name == "{name}" AND chatid == {chat_id}')
    user = CURSOR.fetchone()
    if not user is None:
        return True
    else:
        return False

def get_updates(update_id):
    resp = requests.get(URL+"getUpdates", params={'offset': update_id})
    data = resp.json()
    updates = data['result']
    return updates


def send_message(chat_id,text,keyboard=None):
    params = {
        'chat_id': chat_id, 
        'text':text,
    }

    if not keyboard is None:
        params["reply_markup"] = json.dumps(keyboard)

    requests.get(URL+"sendMessage", params=params)

def send_photo(chat_id, image_url):
    params = {
        'chat_id': chat_id, 
        'photo':image_url,
    }
    requests.get(URL+"sendPhoto",params=params)

def handle_commands(command,chat_id,name):
    global on_bot
    if command == "/start":
        keyboard = {
            "keyboard": [
                ["get image"]
            ],
            "resize_keyboard": True,
        }    
        if user_check(chat_id,name) == True:
            send_message(chat_id,"Wellcome back!",keyboard)
        else:  
            keyboard['keyboard'].append(["/info"])
            send_message(chat_id,"Hello, nice to meet you!",keyboard)
            add_user(chat_id,name)
    elif command =="/info":
        send_message(chat_id,"This bot can send imeges baised on your description.")
    else:
        send_message(chat_id, f"I don't know how to reply to that.")

def handler_message(text,chat_id,name):
    if chat_id in get_description_img:
        params = {
            'key':'44997373-6352c4717bad20cdc4450888a',
            'q':text,
            'image_type': 'photo'
        }
        resp = requests.get(f"https://pixabay.com/api/",params=params)
        if resp.status_code == 200:
            data = resp.json()
            send_photo(chat_id,data['hits'][0]["webformatURL"])
            get_description_img.remove(chat_id)
    else:
        if text.lower() == "get image":
            get_description_img.append(chat_id)
            send_message(chat_id, f"Description image pls: ")
        else:
            send_message(chat_id, f"I don't know how to reply to that.")


def handler_callback(text,chat_id,name):
    if text == "":
        pass

if __name__ == "__main__":
    update_id = None
    initial_db()
    print("Bot start")
    while on_bot:
        for update in get_updates(update_id):
            update_id = update['update_id'] + 1
            if 'callback_query' in update:
                chat_id =update['callback_query']['message']['chat']['id']
                name = update['callback_query']['message']['chat']['first_name']
                text =  update['callback_query']['data']
                handler_callback(text,chat_id,name)
            else:
                chat_id = update['message']['from']['id']
                name = update['message']['from']['first_name']
                text = update['message']['text']

                if text.startswith('/'):
                    handle_commands(text,chat_id,name)
                else:
                    handler_message(text,chat_id,name)   
        time.sleep(1)
    print("Bot stopped")