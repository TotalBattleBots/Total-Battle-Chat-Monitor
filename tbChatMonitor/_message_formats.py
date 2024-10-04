import json
from typing import List, Dict
import discord
from _journal import format_journal
from _tob_constants import static_id_map, keywords

ratfuck_merc_exchange_hook = "https://discord.com/api/webhooks/1145937427886784523" \
                             "/7T1blnLLpNJjICYZYq2EzQPftOKGBdnRO_PcEyFyDvUTytJ-o1T3rd68IS2gc0coJJqY"


def post_ratfuck_message(message: str = ""):
    return
    webhook = discord.SyncWebhook.from_url(ratfuck_merc_exchange_hook)
    webhook.send(message)


def check_keywords(message: str = "") -> List:
    match_words = []
    for keyword in keywords:
        if keyword.lower() in message.lower() and f"{keyword.lower()}:" not in message.lower():
            match_words.append(keyword)
    return match_words


def get_type_by_staticid(static_id: int = 0) -> str:
    return static_id_map.get(static_id, "-UNKNOWN-")


def format_journal_message(data_journal: Dict) -> str:
    c_type = data_journal["entryType"]
    c_name = data_journal["name"]
    c_entry_id = data_journal.get("entryId", None)
    message = format_journal(c_entry_id)
    return message


def format_coords(data_coords: Dict) -> tuple[str, str | None]:
    c_type = data_coords["type"]
    c_x = data_coords["x"]
    c_y = data_coords["y"]
    c_k = data_coords["realmId"]
    c_name = data_coords["name"]
    id = data_coords["staticId"]
    print(f"COORDS: {json.dumps(data_coords)}")

    if int(id) == 400:
        ratfuck_message = f"Mercinary Exchange at K:{c_k} X:{c_x} Y:{c_y}"
    else:
        ratfuck_message = None

    return f"[LINK COORDS: {c_type}] K:{c_k} X:{c_x} Y:{c_y} - {c_name} - {get_type_by_staticid(id)}],", ratfuck_message


def format_epic_monster(data_coords: Dict) -> str:
    c_x = data_coords["x"]
    c_y = data_coords["y"]
    c_k = data_coords["realmId"]
    id = data_coords["staticId"]
    print(f"EPIC MONSTER: {json.dumps(data_coords)}")
    message = f"\n**** EPIC MONSTER SPAWN: K:{c_k} X:{c_x} Y:{c_y} - {get_type_by_staticid(id)}****\n"

    return message


def format_attack_or_scout(journal_id: int) -> str:
    journal_items_message = format_journal(journal_id)


def is_hidden(message: Dict) -> bool:
    data = message.get("data", None)
    if data:
        message_data = json.loads(message["data"])
        hidden_flag = message_data.get("hidden", False)
        return hidden_flag
    else:
        return False
