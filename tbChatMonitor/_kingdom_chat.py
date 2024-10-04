import sys
if __name__ == "__main__":
    sys.path.append(".")

import json
import time
import discord
import pickle
from _tb_message_api import get_tb_messages, list_users_in_chat
from _message_formats import format_journal_message, format_coords, format_epic_monster, check_keywords, is_hidden, \
    post_ratfuck_message
import random
from _post_message import send_epic_link

epic_monster_webhook = "https://discord.com/api/webhooks/1142205416000983181" \
                       "/-FNIXk8fuNI7dnVj666YV2Pej6WVse4di_8y0EX31G9rnw79_FQZfJasG5vicBH_KRyg"

discord_webhooks = {
}

top_message = {
}

credentials = {

}


def _save_config_to_file():
    global credentials
    global discord_webhooks

    save_data = {
        'credentials': credentials,
        'webhooks': discord_webhooks
    }

    open("_kingdom_chat_config.json", 'w').write(json.dumps(save_data, indent=4))


def _load_config_from_file():
    global credentials
    global discord_webhooks

    with open("_kingdom_chat_config.json", "r") as f:
        save_data: dict = json.load(f)

    credentials = save_data.get("credentials", {})
    discord_webhooks = save_data.get("webhooks", {})


def save_state():
    state = {
        "top_message": top_message
    }

    open("_kingdom_chat.dat", "wb").write(pickle.dumps(state))


def load_state():
    global top_message

    try:
        state_pickle = open("_kingdom_chat.dat", "rb").read()
        state = pickle.loads(state_pickle)
        top_message = state["top_message"]
        print(top_message)
    except FileNotFoundError:
        top_message = {}


ignore_kingdom_monsters = [70, 82, 51, 86, 56, 64, 87, 83, 96, 500]


def post_message_to_discord_for_kingdom(kingdom=87, message="Reporting for Duity!"):
    kingdom_webhook = discord_webhooks[kingdom]
    if type(kingdom_webhook) is type([]):
        for one_kingdom_webhook in kingdom_webhook:
            post_message_to_discord(one_kingdom_webhook,message)
    else:
        post_message_to_discord(kingdom_webhook, message)


def post_message_to_discord(kingdom_webhook, message):
    webhook = discord.SyncWebhook.from_url(kingdom_webhook)
    tries = 3
    while tries:
        try:
            webhook.send(message)
            break
        except Exception:
            time.sleep(1)


def post_monster_to_discord(message="Reporting for Duity"):
    webhook = discord.SyncWebhook.from_url(epic_monster_webhook)
    tries = 3
    while tries:
        try:
            webhook.send(message)
            break
        except Exception:
            time.sleep(1)


def post_monster_to_game(message_subs=None):

    if not message_subs:
        return
    response = send_epic_link(message_subs)
    print(f"sent_epic_link: {json.dumps(response, indent=4)} ")


def get_kingdom_messages(kingdom_number, session_key, access_token, timestamp):
    """

    :param kingdom_number:
    :param session_key:
    :param access_token:
    :return:
    """

    kingdom_message_path = f"/v3/group_channels/triumph_realm_channel_{kingdom_number}"
    return get_tb_messages(kingdom_message_path,
                           session_key=session_key,
                           access_token=access_token,
                           time_stamp=timestamp)


from typing import List, Union


def _kingdom_chat_members(kingdom_number: int = 87) -> Union[List[dict], None]:
    chat_path = f"triumph_realm_channel_{kingdom_number}"

    if str(kingdom_number) not in credentials.keys():
        return []

    kingdom_members = list_users_in_chat(chat_url=chat_path,
                                         session_key=credentials[str(kingdom_number)]["session_key"],
                                         access_token=credentials[str(kingdom_number)]['access_token'],
                                         do_join=False)

    return kingdom_members


def _kingdom_messages(kingdom=87):
    try:
        message_ts = 9007199254740991
        current_top_message = top_message.get(kingdom, 0)
        discord_messages = []

        while True:
            data = get_kingdom_messages(kingdom_number=kingdom,
                                        session_key=credentials[kingdom]["session_key"],
                                        access_token=credentials[kingdom]["access_token"],
                                        timestamp=message_ts
                                        )

            error = data.get("error", False)
            if error:
                break

            message_list = data.get("messages", [])
            if not message_list:
                print(json.dumps(data, indent=4))
            new_message_ts = message_list[-1]['created_at']
            for message in message_list:
                message_id = message["message_id"]

                if message_id <= current_top_message:
                    continue

                discord_messages.insert(0, format_kingdom_message(kingdom, message))
                if message_id > top_message.get(kingdom, 0):
                    top_message[kingdom] = message_id

            print(f"k{kingdom}: top_message: {top_message[kingdom]}  message_ts: {message_ts}")
            if current_top_message == 0 or new_message_ts < message_ts:
                break

        for one_discord_message in discord_messages:
            post_message_to_discord_for_kingdom(kingdom=kingdom, message=one_discord_message)
            print(one_discord_message)
            kw = check_keywords(one_discord_message)
            if kw:
                post_message_to_discord_for_kingdom(kingdom=kingdom, message=f"** @everyone - Keywords Detected - {kw}")
    finally:
        save_state()


def format_kingdom_message(kingdom: int, message: str):
    message_type = message["type"]
    if message_type == "MESG":
        message_user = message["user"]["nickname"]
        message_user_clan = (message['user']['metadata']['memberInfo'].split(','))[-1]
        if message["data"] != "":
            message_data = json.loads(message["data"])
            try:
                if message_data.get("eventName", None) and message_data.get("message"):
                    message_text = f"{message_data.get('eventName', '')}: {message_data.get('message')}"

                elif message_data["subs"][message["message"]]["type"] == "coord":
                    if message_user == "Administration":
                        message_text = format_epic_monster(
                            message_data["subs"][message["message"]])
                        if int(kingdom) not in ignore_kingdom_monsters:
                            post_monster_to_discord(message_text)
                    else:
                        message_text, rfm = format_coords(message_data["subs"][message["message"]])
                        if rfm:
                            post_ratfuck_message(rfm)
                elif message_data["subs"][message["message"]]["type"] == "journal":
                    message_text = format_journal_message(message_data["subs"][message["message"]])
                else:
                    message_text = json.dumps(message_data["subs"][message["message"]], indent=4)
            except KeyError as e:
                print(f"Exception - {str(e)}")
                message_text = f"UNKNOWN MESSAGE - JSON FOLLOWS - {json.dumps(message_data)}"
            except Exception as e:
                print(f"Unknown Exception - {str(e)}")
                message_text = f"Message Parse Error - Exception Occured - JSON FOLLOWS - {json.dumps(message_data)}"
        else:
            message_text = message["message"]
    else:
        message_user = "UNDEFINED"
        message_user_clan = "UNDEFINED"
    if message_user == "Administration":
        discord_message = message_text
    else:
        discord_message = f"{'(HIDDEN)' if is_hidden(message) else ''}" + \
                          f"[{message_user_clan}] {message_user}: {message_text}"
    return discord_message


def post_kingdom_messages():
    _load_config_from_file()
    load_state()
    for k in credentials.keys():
        try:
            print(f"Kingdom {k} -----------------------------------------------------------------------")
            _kingdom_messages(k)
        except Exception:
            pass


if __name__ == "__main__":
    while True:
        post_kingdom_messages()
        time.sleep(random.randint(60, 120))
else:
    _load_config_from_file()
