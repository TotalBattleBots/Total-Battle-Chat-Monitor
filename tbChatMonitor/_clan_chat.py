import sys
if __name__ == "__main__":
    sys.path.append(".")


import json
import time
import discord
import pickle
from _tb_message_api import get_tb_messages, list_users_in_chat
from _message_formats import format_journal_message, format_coords, check_keywords, post_ratfuck_message
import random
import datetime
from typing import Union, List

clan_rank = {
    1: "Leader",
    2: "Superior",
    3: "Officer",
    4: "Veteran",
    5: "Soldier"
}


def get_clan_chat_messages(clan_channel_number, session_key, access_token):
    """

    :param clan_channel_number:
    :param session_key:
    :param access_token:
    :return:
    """

    clan_message_path = f"/v3/group_channels/triumph_clan_channel_{clan_channel_number}"

    messages = get_tb_messages(clan_message_path, session_key, access_token)
    return messages


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

    open("_clan_chat_config.json", 'w').write(json.dumps(save_data, indent=4))


def _load_config_from_file():
    global credentials
    global discord_webhooks

    with open("_clan_chat_config.json", "r") as f:
        save_data: dict = json.load(f)

    credentials = save_data.get("credentials", {})
    discord_webhooks = save_data.get("webhooks", {})


def save_state():
    state = {
        "top_message": top_message
    }

    open("_clan_chat.dat", "wb").write(pickle.dumps(state))


def load_state():
    global top_message

    try:
        state_pickle = open("_clan_chat.dat", "rb").read()
        state = pickle.loads(state_pickle)
        top_message = state["top_message"]
        print(top_message)
    except FileNotFoundError:
        top_message = {}


def post_message_to_discord_for_clan(clan_number, message="Reporting for Duity!"):
    clan_webhook = discord_webhooks[clan_number]
    if type(clan_webhook) is type([]):
        for one_clan_webhook in clan_webhook:
            post_message_to_discord(one_clan_webhook, message)
    else:
        post_message_to_discord(clan_webhook,message)


def post_message_to_discord(clan_webhook, message):
    webhook = discord.SyncWebhook.from_url(clan_webhook)
    tries = 3
    while tries:
        try:
            webhook.send(message)
            break
        except Exception:
            time.sleep(1)


def _clan_chat_members(clan_number: int = 0) -> Union[List[dict], None]:
    chat_path = f"triumph_clan_channel_{clan_number}"

    if str(clan_number) not in credentials.keys():
        return []

    clan_members = list_users_in_chat(chat_url=chat_path,
                                      session_key=credentials[str(clan_number)]["session_key"],
                                      access_token=credentials[str(clan_number)]['access_token'],
                                      do_join=False)

    return clan_members


def get_clan_messages(clan_number, session_key, access_token):
    """

    :param clan_number:
    :param session_key:
    :param access_token:
    :return:
    """

    kingdom_message_path = f"/v3/group_channels/triumph_clan_channel_{clan_number}"
    return get_tb_messages(kingdom_message_path, session_key, access_token)


def _clan_messages(clan=87):
    try:
        data = get_clan_messages(clan_number=clan,
                                 session_key=credentials[clan]["session_key"],
                                 access_token=credentials[clan]["access_token"],
                                 )

        current_top_message = top_message.get(clan, 0)
        message_list = data.get("messages", [])
        if not message_list:
            print(json.dumps(data, indent=4))
        message_list.reverse()
        for message in message_list:
            message_id = message["message_id"]
            if message_id <= current_top_message:
                continue

            discord_message = format_clan_message(message, credentials[clan].get("ratfuck", False))

            post_message_to_discord_for_clan(clan_number=clan, message=discord_message)

            kw = check_keywords(discord_message)
            if kw:
                post_message_to_discord_for_clan(clan_number=clan, message=f"** @everyone - Keywords Detected - {kw}")
            print(discord_message)
            top_message[clan] = message_id
    finally:
        save_state()


def format_clan_message(message, ratfuck):
    message_text = ""
    message_type = message["type"]
    if message_type == "MESG":
        message_user = message["user"]["nickname"]
        message_user_clan = (message['user']['metadata']['memberInfo'].split(','))[-1]
        message_user_rank = clan_rank.get(int((message['user']['metadata']['memberInfo'].split(','))[-2]), "UNK")
        if message["data"] != "":
            message_data = json.loads(message["data"])
            try:
                if message_data["subs"][message["message"]]["type"] == "coord":
                    message_text, rfm = format_coords(message_data["subs"][message["message"]])
                    if rfm and ratfuck:
                        post_ratfuck_message(rfm)
                elif message_data["subs"][message["message"]]["type"] == "journal":
                    message_text = format_journal_message(message_data["subs"][message["message"]])
                else:
                    message_text = json.dumps(message_data["subs"][message["message"]], indent=4)
            except KeyError as e:
                message_text = f"UNKNOWN MESSAGE - JSON FOLLOWS - {json.dumps(message_data)} - {str(e)}"
        else:
            message_text = message["message"]
    else:
        message_user = "UNDEFINED"
        message_user_clan = "UNDEFINED"
        message_user_rank = "UNKNOWN"
    discord_message = f"[{message_user_clan}] ({message_user_rank}) {message_user}: {message_text}"
    return discord_message


def post_clan_messages():
    _load_config_from_file()
    load_state()
    for k in credentials.keys():
        print(
            f"Clan {k}: {credentials[k]['clan_name']}--------- {datetime.datetime.now()} --------------------------------------------------------")
        _clan_messages(k)
        time.sleep(random.randint(5, 15))


if __name__ == "__main__":
    while True:
        post_clan_messages()
        time.sleep(random.randint(60, 120))
else:
    _load_config_from_file()