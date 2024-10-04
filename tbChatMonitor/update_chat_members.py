import datetime
import jsonpickle
import os
from _tb_message_api import list_users_in_chat
import concurrent.futures
import threading

c_dict = {}

chat_save_file = "chat_list_data.json"
chat_count = 0
chat_count_lock = threading.Lock()

def save_state():
    open(chat_save_file, "w").write(jsonpickle.dumps(c_dict))


def load_state():
    global c_dict
    if os.path.exists(chat_save_file):
        c_dict = jsonpickle.loads(open(chat_save_file, "r").read())
        print(f"Loaded {len(c_dict)} chats.")


def update_chat_members(chat_key):
    global chat_count

    chat = c_dict[chat_key]

    members = list_users_in_chat(chat['channel_url'])
    with chat_count_lock:
        chat_count += 1
        print(f"f{chat_count}")
    chat['member_list'] = members


if __name__ == '__main__':
    load_state()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as exec:
        exec.map(update_chat_members, c_dict)

    save_state()
