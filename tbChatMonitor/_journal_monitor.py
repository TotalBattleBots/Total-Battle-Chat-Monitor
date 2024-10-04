import sys

if __name__ == "__main__":
    sys.path.append(".")

from _journal import format_journal, get_journal_data_by_id, get_journal_entry_ids
from _journal import BATTLE_ENTRY, BATTLE_SHIELDED_ENTRY, PORTAL_BATTLE_ENTRY, BATTLE_NO_MONSTERS
from _journal import CLAN_ANNOUNCEMENT_ENTRY, ANNOUNCEMENT_ENTRY, SCOUT_ENTRY, CARAVAN_ENTRY, CRYPT_EVENT
from _journal import _journal_get_entry_type, timestamp_n_days_ago, _get_journal_ts_from_journal_result
import pickle
import time
import datetime
import discord
import random

default_journal_entry_types = [BATTLE_SHIELDED_ENTRY, BATTLE_ENTRY, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY, CARAVAN_ENTRY,
                               CLAN_ANNOUNCEMENT_ENTRY, BATTLE_NO_MONSTERS]
current_state = {

}

_journals = {
    "5400038e6e": {
        "description": "[GoD] Thordirne",
        "webhook": "https://discord.com/api/webhooks/1156628436962529280/ChZ4nP"
                   "-723Qin8ON3WtMxHSSeYqmORNKtgWuAcIkYrzentoDlARe9XsJiY4Ew2i1INrX",
        "disabled": False,
        "entry_types": [BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY,
                        ANNOUNCEMENT_ENTRY]
    },
    "4e0002bf94": {
        "webhook": "https://discord.com/api/webhooks/1156633468156006460/tqrgiQLWmyopPx"
                   "-exJSBqT7vZxjTx5F7hbwlghRliyC9Y5pWMy2xItyKmLtqqk6dyd1_",
        "description": "[FoC] Sun Wu master of Scouts and Bubbles",
        "entry_types": default_journal_entry_types,
        "disabled": False,
    },
    "4600016700": {
        "description": "[GoD] Ghost Assasin",
        "webhook": "https://discord.com/api/webhooks/1156664643918512301/sjeZNqvtwSs"
                   "-8aa3DmH0hwxzOfXRF9Q5LpTdhj116HVojK_y_JSs_h47odm9BMj8dbhh",
        "disabled": False,
        "entry_types": [BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY]
    },
    "46000511a2": {
        "description": "[GoD] Ghost Mimo",
        "webhook": "https://discord.com/api/webhooks/1158428934032081037"
                   "/6AFDHH5ibsQ0yBRPHEck7ha9ywdEQW6rZvtMr_CRvmWkFnsTiBxPtn-zkemMU2W9sS8P",
        "disabled": False,
        "entry_types": [BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY]
    },
    "4c0001a2e2": {
        "description": "[GoD] Blood Rhena",
        "webhook": "https://discord.com/api/webhooks/1158495846510379170/UxqvG1yp5jJ4muKXolJVli7nOoMA7"
                   "-lcMi7yRoHYSsowlwo1dZ4QVSCJB4QnLidCe1E0",
        "disabled": False,
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY]
    },
    "7100021655": {
        "description": "Agent of SHIELD - Observer on K82",
        "webhook": "https://discord.com/api/webhooks/1156771100919865454/-eM9snAWtlm6fVsKMPAnOkdr6JgeYdo"
                   "-2nZRaoz22tOXScBLqaSpJ6NR9Tj94S_tR7RR",
        "entry_types": [BATTLE_SHIELDED_ENTRY, SCOUT_ENTRY],
        "disabled": False
    },
    "760000f061": {
        "description": "Agent of SHIELD - Observer on K83",
        "webhook": "https://discord.com/api/webhooks/1156771100919865454/-eM9snAWtlm6fVsKMPAnOkdr6JgeYdo"
                   "-2nZRaoz22tOXScBLqaSpJ6NR9Tj94S_tR7RR",
        "entry_types": [BATTLE_SHIELDED_ENTRY, SCOUT_ENTRY],
        "disabled": False
    },
    "76000112de": {
        "description": "Agent of SHIELD - Observer on K96",
        "webhook": "https://discord.com/api/webhooks/1156771100919865454/-eM9snAWtlm6fVsKMPAnOkdr6JgeYdo"
                   "-2nZRaoz22tOXScBLqaSpJ6NR9Tj94S_tR7RR",
        "entry_types": [BATTLE_SHIELDED_ENTRY, SCOUT_ENTRY],
        "disabled": False
    },
    #    "76000112de": {
    #        "description": "Agent of SHIELD - Observer on K95",
    #        "webhook": "https://discord.com/api/webhooks/1156771100919865454/-eM9snAWtlm6fVsKMPAnOkdr6JgeYdo-2nZRaoz22tOXScBLqaSpJ6NR9Tj94S_tR7RR",
    #        "entry_types": [BATTLE_SHIELDED_ENTRY, SCOUT_ENTRY],
    #        "disabled": False
    #    },
    "720003268e": {
        "description": "Agent of SHIELD - Observer on K99",
        "webhook": "https://discord.com/api/webhooks/1156771100919865454/-eM9snAWtlm6fVsKMPAnOkdr6JgeYdo"
                   "-2nZRaoz22tOXScBLqaSpJ6NR9Tj94S_tR7RR",
        "entry_types": [BATTLE_SHIELDED_ENTRY, SCOUT_ENTRY],
        "disabled": False
    },
    "5200030151": {
        "description": "Agent of SHIELD - Daddy Shark Shield Checks",
        "webhook": "https://discord.com/api/webhooks/1166219468549144667"
                   "/pD0KL2zIiI0o31X3ZozU8n9djAXxb4U6qiEL1YjHpCJprt4Pu_nPpFZM18YT97xZqUqH",
        "entry_types": [BATTLE_SHIELDED_ENTRY, BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False
    },
    "520000265a": {
        "description": "Agent of SHIELD - Daddy Shark Shield Checks",
        "webhook": "https://discord.com/api/webhooks/1173115118113017939/Z8WqfbReok-3YdD_PzYUwnf4yo-gO-bwuTBXoshmjY1z3E8ExT2aI7iM6NcQrT9FD0bp",
        "entry_types": [BATTLE_SHIELDED_ENTRY, BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False
    },
    "4b000735f1": {
        "description": "[GOD] Space",
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False,
        "webhook": "https://discord.com/api/webhooks/1157350999867019317"
                   "/Um114lqlZYApYjUDdTNbcnsXZsbFFGP9ll22IvWHn47Rts7_wvCoZ9gh55VPbs86135s",
    },
    "340000bc94": {
        "webhook": "https://discord.com/api/webhooks/1162061135718121492/QfGp1v09jF16yuzex5DSxq2IsPiOZNT"
                   "-p50YkuStGlgfkssXAVAExZwOR0o8xaQ2CTnD",

        "description": "[IYI] Sinan",
        "disabled": False,
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY],
    },

    "4b0000d451": {
        "webhook": "https://discord.com/api/webhooks/1163310062249459723/fjzzAZA4I09BcvIL-ZiXeEp2tMs2tjA5Tv_aS"
                   "-LW2FwkDXZuh0uTt6ZtUInjFewO67Ru",

        "description": "Attacked Forts",
        "disabled": False,
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY],
    },

    "4a00046a7d": {
        "description": " - UNKNOWN - ",
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False,
        "webhook": "https://discord.com/api/webhooks/1164035018197319700"
                   "/ydT6169h3eCY_sYPrOj5vQtlPMHEKbKKKeGCBH21Ii8sLAGD7eST3Ajceoq8Dr-G_6cn",
    },
    "630000ef11": {
        "description": "[BBX] KEV",
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False,
        "webhook": "https://discord.com/api/webhooks/1170810159581376522/Xd_AHfojoINGeMS_XsowOHgMfqWp5mDgmfXUhIhNmiub5dQON8QBf7LQ6MdzZfQFUNbw"
    },
    "630000733c": {
        "description": "[KUB] OWL",
        "entry_types": [BATTLE_ENTRY, SCOUT_ENTRY, BATTLE_NO_MONSTERS, PORTAL_BATTLE_ENTRY, CLAN_ANNOUNCEMENT_ENTRY,
                        ANNOUNCEMENT_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False,
        "webhook": "https://discord.com/api/webhooks/1170881069952815134/-z5UIERKLXIoUgyxnwYJfDXyIoguMAy1BSonAHvYLAoiebtEKVd_gVptKywQ2esm4mnl"
    },
    "530002d30e": {
        "description": "Agent of SHIELD - Sir Brad",
        "ninja": False,
        "webhook": "https://discord.com/api/webhooks/1170030754462445671/ImD1JDdh9JVrBP5J4_dkt7iexZ9IMprD8BsPmIo9d2sv1w-SpzIPkK5Js0bBeN6RqZDI",
        "entry_types": [BATTLE_SHIELDED_ENTRY, BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False
    },
    "4e0000461b": {
        "description": "Agent of SHIELD - Asada",
        "webhook": "https://discord.com/api/webhooks/1170031590877970433/K5LvkbJAnT_T7GGcxlAGDn3hm8yWwXAzNEs_C-1JbynIQ35TzycVOty8VPsGi5W5v9Ne",
        "entry_types": [BATTLE_SHIELDED_ENTRY, BATTLE_ENTRY, BATTLE_NO_MONSTERS, SCOUT_ENTRY, PORTAL_BATTLE_ENTRY,
                        CARAVAN_ENTRY],
        "disabled": False
    },

}


# Shield Reports Chat
# https://discord.com/api/webhooks/1156771100919865454/-eM9snAWtlm6fVsKMPAnOkdr6JgeYdo-2nZRaoz22tOXScBLqaSpJ6NR9Tj94S_tR7RR


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


def save_state():
    state = {
        "current_state": current_state
    }

    open("_journal_monitor_state.dat", "wb").write(pickle.dumps(state))


def post_message_to_discord_for_user(player_id, message="Reporting for Duity!"):
    webhook_url = _journals[player_id]['webhook']
    if type([]) is type(webhook_url):
        for one_webhook_url in webhook_url:
            post_message_to_discord(message, one_webhook_url)
    else:
        post_message_to_discord(message, webhook_url)


def post_message_to_discord(message, webhook_url):
    lines = split_string_on_newline(message, 1900)
    webhook = discord.SyncWebhook.from_url(webhook_url)
    for line in lines:
        tries = 3
        while tries:
            try:
                webhook.send(line)
                break
            except Exception:
                time.sleep(1)


def load_state():
    global current_state
    try:
        state_pickle = open("_journal_monitor_state.dat", "rb").read()
        state = pickle.loads(state_pickle)
        current_state = state["current_state"]
    except FileNotFoundError:
        current_state = {}


def monitor_journal(player_id: str = None):
    global _journals
    top_journal_id = current_state.get(player_id, 0)
    if not top_journal_id:
        j_result: dict = get_journal_entry_ids(player_id)
        if not j_result:
            print(f"No Journal Results for {player_id}")
            return

        entry_list: list[dict] = j_result.get('result', {}).get('entries', [])
        if not entry_list:
            print(f"No entry list for {player_id}")
            return

        try:
            top_journal_id = entry_list[-1].get('entry_id', None)
        except IndexError:
            top_journal_id = None
        if not top_journal_id:
            print(f"No journal ids found")
            return

    j_result_ids = get_journal_entry_ids(player_id, current_min=top_journal_id)
    e_list = j_result_ids['result']['entries']

    if e_list:
        entry_ids = sorted([item['entry_id'] for item in e_list])
        for entry_id in entry_ids:
            journal_data = get_journal_data_by_id(entry_id)
            if not journal_data:
                print(f"No journal data for entry {entry_id}")
                continue

            entry_type = _journal_get_entry_type(journal_data)
            if entry_type in _journals[player_id].get("entry_types", []):
                print(f"Getting Journal entry for: {entry_id} of type {entry_type}")

                if entry_type == BATTLE_ENTRY and BATTLE_NO_MONSTERS in _journals[player_id].get("entry_types", []):
                    result_message = format_journal(entry_id, no_monsters=True)
                else:
                    result_message = format_journal(entry_id)
                if result_message:
                    post_message_to_discord_for_user(player_id, "-" * 80 + "\n" + result_message)
            else:
                print(f"Skipping Journal Entry of type {entry_type}")
            top_journal_id = entry_id

        current_state[player_id] = top_journal_id + 1
        save_state()


def post_journals():
    load_state()
    for k in _journals.keys():
        disabled = _journals[k].get("disabled", False)
        print(
            f"Journal: [{_journals[k]['description']}]  ------- {datetime.datetime.now()}"
            "------------------------------")
        if disabled:
            print("Disabled")
            continue

        monitor_journal(k)


def dump_journal(player_id: str, max_entries: int = 100, days: int = 1, journal_type_list=default_journal_entry_types,
                 include_deleted=False, include_starred=False, csv_output=True):
    terminal_ts = timestamp_n_days_ago(days) if days else None
    entries_count = 0
    journal_result_message = ""
    least_entry = 0

    class BreakOut(Exception):
        pass

    try:

        while True:
            j_result: dict = get_journal_entry_ids(player_id, current_max=least_entry, include_deleted=include_deleted,
                                                   include_starred=include_starred)
            if not j_result:
                break

            entry_list: list[dict] = j_result.get('result', {}).get('entries', [])
            if not entry_list:
                print(f"No entry list for {player_id}")
                break

            bottom_entry = entry_list[0].get('entry_id', None)

            entry_list.reverse()
            for entry in entry_list:
                entries_count += 1
                entry_id = entry['entry_id']
                entry_data = get_journal_data_by_id(entry['entry_id'])
                entry_type = _journal_get_entry_type(entry_data)
                if entry_type in journal_type_list:
                    journal_result_message += format_journal(journal_entry=entry_id, csv_output=csv_output)
                else:
                    journal_result_message += f"Skipping Journal Entry {entry_id} of type {entry_type}\n"
                if max_entries and entries_count > max_entries:
                    raise BreakOut

            least_entry = bottom_entry - 1
            entry_data = get_journal_data_by_id(bottom_entry)
            bottom_entry_ts = _get_journal_ts_from_journal_result(entry_data)
            print(f"bottom_entry_ts: {bottom_entry_ts} terminal_ts: {terminal_ts}")
            if not bottom_entry_ts or (terminal_ts and bottom_entry_ts < terminal_ts):
                break
    except BreakOut:
        pass

    return journal_result_message


if __name__ == "__main__":
    #    _save_config_to_file()
    while True:
        post_journals()
        time.sleep(random.randint(5, 15))
