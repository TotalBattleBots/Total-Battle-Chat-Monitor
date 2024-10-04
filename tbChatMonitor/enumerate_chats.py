from _list_chats import list_chats
import json
import requests
import sys
from urllib import parse
from typing import Dict, List
import datetime
import jsonpickle
import os
import time
from _tb_message_api import list_users_in_chat
import concurrent.futures
import threading

c_dict = {}
c_dict_lock = threading.Lock()
channel_count = 0
channel_total = 0
chat_save_file = "chat_list_data.json"


def save_state():
    open(chat_save_file, "w").write(jsonpickle.dumps(c_dict))


def load_state():
    global c_dict
    if os.path.exists(chat_save_file):
        try:
            c_dict = jsonpickle.loads(open(chat_save_file, "r").read())
        except Exception:
            pass


def enumerate_chat(chat_pattern):
    global c_dict
    global channel_total
    global channel_count

    channels = list_chats(chat_pattern)

    channel_total = len(channels)
    channel_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as exec:
        exec.map(enumerate_process_chat, channels)


def enumerate_process_chat(one_channel):
    global c_dict
    global channel_count
    channel_name = one_channel.get("name", "---NONAME---")

    channel_url = one_channel.get("channel_url", "")
    last_message = one_channel.get("last_message", None)
    if last_message:
        last_message_time = datetime.datetime.utcfromtimestamp(last_message.get('created_at', 0) / 1000)
    else:
        last_message_time = 0

    with c_dict_lock:
        channel_count += 1
        t_c = c_dict.get(channel_name, None)

    if t_c is not None:
        print(f"{channel_count}/{channel_total}: Chat {channel_name} exists.")
        t_c["last_message"] = last_message
        t_c["last_message_time"] = last_message_time
        t_c["last_seen_time"] = time.time()
        with c_dict_lock:
            c_dict[channel_name] = t_c

    else:
        print(f"{channel_count}/{channel_total}:Chat {channel_name} does not exist")
        try:
            created_by = one_channel.get("created_by", {"nickname": "--DELETED USER--"}).get("nickname", "--DELETED USER--")
        except Exception:
            created_by = "---DELETED-USER---"
        member_list = list_users_in_chat(chat_url=channel_url)

        with c_dict_lock:
            c_dict[channel_name] = {
                "channel_name": channel_name,
                "channel_url": channel_url,
                "created_by": created_by,
                "member_list": member_list,
                "last_message": last_message,
                "last_message_time": last_message_time,
                "last_seen_time": time.time()
            }


if __name__ == '__main__':

    load_state()

    start_number = len(c_dict)

    try:
        if os.path.exists(sys.argv[1]):
            patterns = open(sys.argv[1], "r").readlines()
            patterns = [pattern.strip() for pattern in patterns]
        else:
            patterns = sys.argv[1::]
    except PermissionError:
        patterns = sys.argv[1::]
    except IndexError:
        print("No pattern giving.. Indexing everything.")
        patterns = [""]

    for pattern in patterns:
        enumerate_chat(pattern)
    
    save_state()
    end_number = len(c_dict)

    print(f"{start_number} -> {end_number}")

    if end_number > start_number:
        print(f"{end_number - start_number} new chats discovered.")
