import sys
if __name__ == "__main__":
    sys.path.append(".")


import json
import time
import discord
import pickle
from _tb_message_api import get_tb_messages, join_chat, leave_chat
from _message_formats import format_journal_message, format_coords, check_keywords, is_hidden
from _util import convert_unix_to_utc

import random
import datetime
from typing import List, Any

max_message_ts = 9007199254740991

top_message = {
}

discord_webhooks = {
}

group_chats = {
}


def split_string_on_newline(s, max_bytes=1900):
    # Convert the string to bytes
    s_bytes = s.encode('utf-8')

    # List to store the split strings
    result = []

    # Starting index for each split
    start = 0

    while start < len(s_bytes):
        # If the remaining string is shorter than max_bytes, append it to the result and break
        if len(s_bytes) - start <= max_bytes:
            result.append(s_bytes[start:].decode('utf-8'))
            break

        # Find the end index for the current split
        end = start + max_bytes

        # Backtrack to the last newline
        while end > start and s_bytes[end] != ord('\n'):
            end -= 1

        # If we didn't find a newline, just split at max_bytes
        if end == start:
            end = start + max_bytes

        # Append the split string to the result
        result.append(s_bytes[start:end].decode('utf-8'))

        # Move the start index to the next character after the newline
        start = end + 1 if s_bytes[end] == ord('\n') else end

    return result


def _save_config_to_file():
    global group_chats

    save_data = {
        'group_chats': group_chats,
    }

    open("_group_chat_config.json", 'w').write(json.dumps(save_data, indent=4))


def _load_config_from_file():
    global group_chats

    with open("_group_chat_config.json", "r") as f:
        save_data: dict = json.load(f)

    group_chats = save_data.get("group_chats", {})


def save_state():
    state = {
        "top_message": top_message
    }

    open("_group_chat.dat", "wb").write(pickle.dumps(state))


def load_state():
    global top_message

    try:
        state_pickle = open("_group_chat.dat", "rb").read()
        state = pickle.loads(state_pickle)
        top_message = state["top_message"]
        print(top_message)
        time.sleep(1)
    except FileNotFoundError:
        top_message = {}


def post_message_to_discord(chat_path, message="Reporting for Duty!"):

    if type(chat_path) is type([]):
        for one_chat_path in chat_path:
            post_message_to_discord(one_chat_path,message)
    else:
        try:
            lines = split_string_on_newline(message, 1900)
            webhook = discord.SyncWebhook.from_url(group_chats[chat_path]['webhook'])
            for line in lines:
                for line in lines:
                    tries = 3
                    while tries:
                        try:
                            webhook.send(line)
                            break
                        except Exception:
                            time.sleep(1)

        except Exception as e:
            print(f"Exception posting {group_chats['chat_path']['chat_name']} to discord.  Message: {message} - str{e}")


def get_group_chat_messages(chat_path: str, message_ts: int = max_message_ts):
    """

    :param message_ts:
    :param chat_path:
    :return:
    """

    path = f"/v3/group_channels/{chat_path}"
    messages = get_tb_messages(message_path=path, time_stamp=message_ts)
    return messages


def get_all_group_chat_messages(chat_path: str) -> list[Any] | Any:
    message_ts = max_message_ts
    all_messages = []

    if not join_chat(chat_path=chat_path):
        return []

    try:
        while True:
            result = get_group_chat_messages(chat_path=chat_path, message_ts=message_ts)
            if result:
                messages: List[Any] = result["messages"]
                if messages:
                    message_ts = messages[-1]['created_at']
                    messages.reverse()
                    all_messages = messages + all_messages
                else:
                    break
            else:
                break
    finally:
        leave_chat(chat_path=chat_path)

    return all_messages


def dump_group_chat(chat_path: str) -> List[str]:
    messages_text = []
    messages = get_all_group_chat_messages(chat_path=chat_path)
    for message in messages:
        messages_text.append(format_group_message(message))

    return messages_text


def format_group_message(message, timestamp=True):
    message_text = ""
    message_type = message["type"]
    message_time = message["created_at"]
    if message_type == "MESG":
        message_user = message["user"]["nickname"]
        message_user_clan = (message['user']['metadata']['memberInfo'].split(','))[-1]
        if message["data"] != "":
            message_data = json.loads(message["data"])
            try:
                if message_data.get("eventName", None) and message_data.get("message"):
                    message_text = f"{message_data.get('eventName', '')}: {message_data.get('message')}"
                elif message_data["subs"][message["message"]]["type"] == "coord":
                    message_text, rfm = format_coords(message_data["subs"][message["message"]])
                elif message_data["subs"][message["message"]]["type"] == "journal":
                    message_text = format_journal_message(message_data["subs"][message["message"]])
                else:
                    message_text = json.dumps(message_data["subs"][message["message"]], indent=4)
            except KeyError as e:
                print(f"Exception: {e}")
                message_text = f"UNKNOWN MESSAGE - JSON FOLLOWS - {json.dumps(message_data)}"
        else:
            message_text = message["message"]
    else:
        message_user = "UNDEFINED"
        message_user_clan = "UNDEFINED"

    discord_message = f"{'[' + str(convert_unix_to_utc(message_time)) + ']' if timestamp else ''} " + \
                      f"{'(HIDDEN)' if is_hidden(message) else ''}[{message_user_clan}] {message_user}: {message_text}"
    return discord_message


def monitor_group_chat(chat_path: str):
    try:
        data = get_group_chat_messages(chat_path=chat_path)

        current_top_message = top_message.get(chat_path, 0)
        message_list = data.get("messages", [])
        if not message_list:
            print(json.dumps(data, indent=4))
        message_list.reverse()
        for message in message_list:
            message_id = message["message_id"]
            if message_id <= current_top_message:
                continue

            discord_message = format_group_message(message, timestamp=False)
            post_message_to_discord(chat_path=chat_path, message=discord_message)

            kw = check_keywords(discord_message)
            if kw:
                post_message_to_discord(chat_path=chat_path, message=f"** @everyone - Keywords Detected - {kw}")
            print(discord_message)
            top_message[chat_path] = message_id
    finally:
        save_state()


def post_group_chats():
    _load_config_from_file()
    load_state()
    for k in group_chats.keys():
        disabled = group_chats[k].get("disabled", False)
        if disabled:
            continue
        print(
            f"{group_chats[k]['chat_name']}--------- {datetime.datetime.now()} --------------------------------------")
        monitor_group_chat(k)
        time.sleep(random.randint(1, 5))


if __name__ == '__main__':
    while True:
        post_group_chats()
        time.sleep(random.randint(60, 120))
