import datetime
import json
import time
from datetime import datetime, timedelta

from humanize import intword
from _util import convert_unix_to_utc
import requests
from _model_user import PlayerIdManager
from typing import Dict, List, Union, Any
from _tob_constants import unit_map, contract_items
from _util import compute_difference
from _tob_constants import itemids, static_id_map, monster_level_units, guards_level_units, specs_level_units

import inspect
import sys

items_to_display = [1, 2, 3, 4, 5, 6, 16]


def format_crypt_event(_: Union[dict, int]) -> str:
    return "Cryptic Event"


def format_clan_event(journal_entry: Union[dict, int]) -> str:
    if isinstance(journal_entry, int):
        j_response = get_journal_data_by_id(journal_entry)
    elif isinstance(journal_entry, dict):
        j_response = journal_entry
    else:
        raise TypeError("Expected Dict or Int")

    verb = {
        "clan_kick": "Kicked from",
        "clan_join": "Joined",
        "clan_exit": "Left"
    }

    event_data = j_response.get("result", {}).get("entries", [{}])[0].get("data", {})
    event_name = event_data.get("eventName", "")
    clan_name = event_name.get("name", 'UNKNOWN')
    clan_trigraph = event_data.get("initials", 'UNK')

    message = f"{verb.get(event_name, 'UNK')} clan [{clan_trigraph}] {clan_name}"
    return message


def format_clan_announcement(journal_entry: Union[dict, int]) -> str:
    if isinstance(journal_entry, int):
        j_response = get_journal_data_by_id(journal_entry)
    elif isinstance(journal_entry, dict):
        j_response = journal_entry
    else:
        raise TypeError("Expected Dict or Int")

    try:
        message = j_response["result"]["entries"][0]["data"]["message"]
    except IndexError as e:
        message = ""
        print(f"Exception handling Journal Entry. {str(e)}")
        # print(f"{json.dumps(j_response, indent=4)}")
    return message


def format_treasury_buy(journal_entry: Union[dict, int]) -> str:
    if isinstance(journal_entry, int):
        j_response = get_journal_data_by_id(journal_entry)
    elif isinstance(journal_entry, dict):
        j_response = journal_entry
    else:
        raise TypeError("Expected Dict or Int")

    result_string = json.dumps(j_response, indent=4)
    return result_string


def _format_allies(journal_entry: dict, attacker: bool = False, full: bool = False, csv_output=False) -> str:
    player_mgr = PlayerIdManager()
    ally_string = ""

    if attacker:
        ally_type = 'attackerAllies'
    else:
        ally_type = 'defAllies'
    try:
        def_allies = journal_entry['data'][ally_type]
        if len(def_allies) > 1:
            for one_ally in def_allies[1:]:
                march_flags = one_ally.get("atom").get("marchInfo").get("marchFlags")
                if int(march_flags) != 98:
                    continue
                player_info = player_mgr.get_player_by_id(
                    PlayerIdManager.encode_user_id(one_ally["guid"][0], one_ally["guid"][1]))

                if csv_output:
                    ally_string = f'{player_info.name},'
                else:
                    ally_string += f"[{player_info.clan_id}] {player_info.name}\n"
                    if full:
                        ally_string += "Units:\n______\n"
                        ally_units = one_ally.get("atom", {}).get("units", {})
                        ally_contracts = one_ally.get("atom", {}).get("contracts", [])
                        ally_string += _format_units(units_list=ally_units, contracts=ally_contracts)
                        ally_string += "\n\n"

        if csv_output:
            ally_string = ally_string[:-1]
        return ally_string
    except KeyError as e:
        print(f"KeyError in Bunker Allies - {str(e)}")
        return ""


def _is_scout_attack(journal_entry: dict) -> bool:
    result = False
    try:
        march_info = journal_entry['data']['attackerAllies'][0]['atom']['marchInfo']
        march_intent = march_info['marchIntent']
        if march_intent == 1:
            result = True
        elif march_intent == 2:
            result = False
        else:
            print(f"=== Unknown March Intent on {journal_entry['result']['entries'][0]['entry_id']} ")
            result = False
    finally:
        return result


def _format_units(units_list: dict,
                  contracts=None) -> str:
    item = 0
    units_list_string = ""
    for unit_id in units_list.keys():
        unit_count = units_list[unit_id].get("count", -1)
        unit_string = unit_map.get(int(unit_id), f"UNKNOWN UNIT {unit_id}")
        units_list_string += f"{unit_string}: {unit_count}".ljust(45)
        item += 1
        if item == 1:
            units_list_string += "\n"
            item = 0
        else:
            units_list_string += " "

    merc_string = _format_merc_units(contracts)
    if merc_string:
        units_list_string += f"\nMercenaries:\n{merc_string}\n"

    return units_list_string


def _get_highest_unit_type(units_list: dict) -> List[int]:
    spec_high = 0
    guardian_high = 0
    monster_high = 0
    for unit_id in units_list.keys():
        for i in range(0, len(monster_level_units)):
            if int(unit_id) in monster_level_units[i] and i > monster_high:
                monster_high = i
                break
        for i in range(0, len(guards_level_units)):
            if int(unit_id) in guards_level_units[i] and i > guardian_high:
                guardian_high = i
                break
        for i in range(0, len(specs_level_units)):
            if int(unit_id) in specs_level_units[i] and i > spec_high:
                spec_high = i
                break

    return [guardian_high + 1, monster_high + 1, spec_high + 1]


def _format_merc_units(contracts: List[Dict]) -> str:
    merc_counts: dict[Any, int | Any] = {}

    for one_contract in contracts:
        count = int(one_contract['count'])
        if count:
            merc_counts[one_contract['itemId']] = merc_counts.get(one_contract['itemId'], 0) + count

    unit_strings = []
    item = 0
    for unit_id, count in merc_counts.items():
        unit_string = contract_items.get(unit_id, f"UNKNOWN MERC {unit_id}")
        formatted_string = f"{unit_string}: {count}".ljust(45)
        unit_strings.append(formatted_string)
        item += 1
        if item == 1:
            unit_strings.append("\n")
            item = 0

    return "".join(unit_strings).strip()


def format_scout_or_attack_journal(journal_entry: Union[dict, int], full=False, no_monsters=False, show_attacker=False, csv_output=False):
    player_mgr = PlayerIdManager()

    if csv_output:
        print("Scout or Attack Report with CSV\n")
    if isinstance(journal_entry, int):
        journal_result = get_journal_data_by_id(journal_entry)
        if not journal_result.get('result', {'entries': []}).get('entries', []):
            print(f"No Journal Found - {journal_entry} - {json.dumps(journal_result,indent=4)}")
            return "No Journal Entry Found"
            
    elif isinstance(journal_entry, dict):
        journal_result = journal_entry
    else:
        raise TypeError("Dict or Int Expected")

    journal_entry = journal_result["result"]["entries"][0]
    defender = journal_entry['data'].get('defAllies', [{}])[0]
    attacker = journal_entry['data'].get('attackerAllies', [{}])[0]

    defender_id = PlayerIdManager.encode_user_id(defender.get("guid", [0, 0])[0],
                                                 defender.get("guid", [0, 0])[1])
    defender_info = player_mgr.get_player_by_id(defender_id)

    attacker_id = PlayerIdManager.encode_user_id(attacker.get("guid", [0, 0])[0],
                                                 attacker.get("guid", [0, 0])[1])
    attacker_info = player_mgr.get_player_by_id(attacker_id)

    item_message = _format_attack_scout_defender_items(journal_result)
    coordinates = _format_attack_get_coordinates(journal_result)
    defender_static_id = int(defender.get('atom', {}).get('info', {}).get('staticId', "2"))
    if full and defender:
        defender_hero_unit_list = (defender.get('atom', {}).get('units', {}))
        defender_hero_contracts_list = defender.get('atom', {}).get('contracts', [])
        defender_hero_unit_list_string = _format_units(units_list=defender_hero_unit_list,
                                                       contracts=defender_hero_contracts_list)

    else:
        defender_hero_unit_list_string = None

    attacker_hero_unit_list = (attacker.get('atom', {}).get('units', {}))
    attacker_high_units = _get_highest_unit_type(attacker_hero_unit_list)

    if full and show_attacker:
        attacker_hero_contracts_list = attacker.get('atom', {}).get('contracts', [])
        attacker_hero_unit_list_string = _format_units(units_list=attacker_hero_unit_list,
                                                       contracts=attacker_hero_contracts_list)

        attacker_high_units = _get_highest_unit_type(attacker_hero_unit_list)
    else:
        attacker_hero_unit_list_string = None

    if defender_static_id > 1000:
        if no_monsters:
            return ""

        defender_id_string = static_id_map.get(defender_static_id,
                                               f"[{defender_info.clan_id}] {defender_info.name}")
    else:
        defender_id_string = f"[{defender_info.clan_id}] {defender_info.name}"

    bunker_allies = _format_allies(journal_entry, attacker=False, full=full, csv_output=csv_output)
    attack_allies = _format_allies(journal_entry, attacker=True, full=full, csv_output=csv_output)
    lost_items = _format_attack_lost_items(journal_result)
    event_name = "scout" if _is_scout_attack(journal_entry) else journal_entry["data"]["eventName"]
    total_silver_remaining = _format_attack_get_silver(journal_entry)
    lost_silver = _format_attack_lost_silver(journal_entry)

    if not csv_output:
        scout_message = \
            f"""
    
    EntryID: {journal_entry["entry_id"]}
    Time: {convert_unix_to_utc(journal_entry["entry_ts"] * 1000)} UTC
    Event Name: {event_name}
    Attacker: [{attacker_info.clan_id}] {attacker_info.name} ({attacker_id})
    Defender: {defender_id_string} ({defender_id})
    Attacker High Units: G{attacker_high_units[0]}, M{attacker_high_units[1]}, S{attacker_high_units[2]}
    Attacker Location: K:{coordinates["attacker"][0]} X:{coordinates["attacker"][1]} Y:{coordinates["attacker"][2]}
    Defender Location: K:{coordinates["defender"][0]} X:{coordinates["defender"][1]} Y:{coordinates["defender"][2]}
    Status: {"Defeat" if journal_entry["data"]["win"] == "false" else "Victory!"}
    """

        if full and show_attacker:
            scout_message += \
                f"""
    Attacker Units:
    -----------
    {attacker_hero_unit_list_string}         
    """

        if attack_allies:
            scout_message += \
                f"""
    Clan March Allies:
    -----------
    {attack_allies}       

        """

        if lost_items:
            scout_message += \
                f"""
    Lost Items In Attack:
    ----------------------
    {lost_items}
    """
        if item_message:
            scout_message += \
                f"""
    Defender Items After Attack:
    ---------------
    {item_message}
    """
        if defender_hero_unit_list_string:
            scout_message += \
                f"""
    Units in the City:
    -----------
    {defender_hero_unit_list_string}
                """
        if bunker_allies:
            scout_message += \
                f"""
    Reinforcements In City:
    --------------
    {bunker_allies}
    
    """

        print(f"@@@@@@ Silver Remaining: {total_silver_remaining}")
        if total_silver_remaining > 1000000000:
            scout_message += "\n@everyone - Lordy get in here, we got a rich one!\n"

        if not full:
            _journal_entry_id = _get_journal_id_from_journal_result(journal_result)
            print(_journal_entry_id)
            scout_message += f"\n\nFor a full scout report: /journal journal_id:{_journal_entry_id}"
        return scout_message
    else:
        if lost_silver:
            if attack_allies:
                attacker_list = f'"{attacker_info.name},{attack_allies}"'
            else:
                attacker_list = attacker_info.name

            csv_message = f"{journal_entry['entry_id']},{journal_entry['entry_ts']},B," + \
                          f"{defender_info.clan_id},{defender_info.name},{attacker_info.clan_id}," + \
                          f"{attacker_list},Silver,{lost_silver}\n"
            return csv_message
        else:
            print(f"lost_silver is 0 - {defender_id_string} - {journal_entry['entry_id']}")
            return ""


def _format_attack_get_coordinates(journal_data):
    result = {"defender": (0, 0, 0), "attacker": (0, 0, 0)}
    try:
        source_coord = journal_data["result"]["entries"][0]["data"]["attackerAllies"][0]["atom"]["info"]["sourceCoord"]
        target_coord = journal_data["result"]["entries"][0]["data"]["attackerAllies"][0]["atom"]["info"]["targetCoord"]

        result["defender"] = (target_coord["realmId"], target_coord["x"], target_coord["y"])
        result["attacker"] = (source_coord["realmId"], source_coord["x"], source_coord["y"])

    except Exception as e:
        print(str(e))
    finally:
        return result


def _format_attack_get_silver(journal_entry):
    total_silver = 0
    try:
        lost_items = journal_entry['data']['defAllies'][0].get('lost', {}).get('items', {})
        j_item = _find_in_json(journal_entry, "itemId", 2)
        lost_items: _find_in_json(journal_entry, key="lost")
        if j_item:
            total_silver = int(j_item[0].get('count', 0))
            if lost_items:
                total_silver -= int(int(lost_items[0].get(str(2), 0)))
    finally:
        return total_silver


def _format_attack_lost_silver(journal_data: dict) -> int:
    lost_silver = 0
    try:
        lost_items = journal_data['data']['defAllies'][0].get('lost', {}).get('items', {})
        lost_silver = int(lost_items.get(str(2), 0))
    finally:
        return lost_silver


def _format_attack_lost_items(journal_data: dict) -> str:
    lost_items_message = ""
    try:
        lost_items = journal_data['result']['entries'][0]['data']['defAllies'][0].get('lost', {}).get('items', {})
        for item in items_to_display:
            try:
                l_item = lost_items.get(str(item), 0)
                if l_item:
                    lost_items_message += f" {itemids[item]}: {intword(l_item)},"
            except Exception as e:
                print(f"a: {str(e)}")
                continue

    except Exception as e:
        print(f"1: {str(e)}")

    if lost_items_message.endswith(','):
        lost_items_message = lost_items_message[1:-1]
    return lost_items_message


def _format_attack_scout_defender_items(journal_data):
    try:
        item_display = []

        lost_items = journal_data['result']['entries'][0]['data']['defAllies'][0].get('lost', {}).get('items', {})
        for item in items_to_display:
            try:
                j_item = _find_in_json(journal_data, "itemId", item)
                item_count = int(j_item[0].get('count', 0))
                item_count -= int(lost_items.get(str(item), 0))
                if item_count < 0:
                    item_count = 0

                item_display.append([itemids[item], item_count])
            except Exception as e:
                print(str(e))
                pass
        message = ""

        for d_item in item_display:
            message += f" {d_item[0]}: {intword(d_item[1])},"

        if message.endswith(','):
            message = message[1:-1]

        return message
    except Exception as e:
        print(str(e))
        return ""


def _find_in_json(obj, key, value=None) -> list:
    """
    Recursively search for a key-value pair in a JSON object.

    :param obj: The JSON object.
    :param key: The key to search for.
    :param value: The value to match.
    :return: A list of matching sub-objects.
    """
    matches = []

    if isinstance(obj, dict):
        if value:
            if key in obj and obj[key] == value:
                matches.append(obj)
        else:
            if key in obj:
                matches.append(obj)

        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                matches.extend(_find_in_json(v, key, value))

    elif isinstance(obj, list):
        for item in obj:
            matches.extend(_find_in_json(item, key, value))

    return matches


def format_bubble_battle(journal_entry: Union[int, dict]):
    result_message = ""
    player_mgr = PlayerIdManager()

    if isinstance(journal_entry, int):
        journal_result = get_journal_data_by_id(journal_entry)
    elif isinstance(journal_entry, dict):
        journal_result = journal_entry
    else:
        raise TypeError("Dict or Int Expected")

    entries = journal_result.get('result', {'entries': []}).get('entries', [])
    if not entries:
        print(f"2 - No Journal Found - {journal_entry} - {json.dumps(journal_result,indent=4)}")
        return "No Journal Entry Found"

    entry_id = entries[0].get('entry_id', 0)
    defender = entries[0].get('data', {}).get('defAllies', [{}])[0]
    # print(defender)
    defender_info = defender.get("atom", {}).get("info", {})
    if not defender_info:
        return "No Defender Found"

    shield_ts_value = defender_info.get("shieldTs", None)
    defender_x = defender_info.get("targetCoord", {}).get("x", 0)
    defender_y = defender_info.get("targetCoord", {}).get("y", 0)
    defender_k = defender_info.get("targetCoord", {}).get("realmId", 0)
    defender_id = PlayerIdManager.encode_user_id(defender.get("guid", [0, 0])[0],
                                                 defender.get("guid", [0, 0])[1])
    defender_id_info = player_mgr.get_player_by_id(defender_id)

    if shield_ts_value:
        delta_days, delta_hours, delta_minutes = compute_difference(shield_ts_value)
        result_message = f"""
        
EntryID: {entry_id}
Player: [{defender_id_info.clan_id}] {defender_id_info.name}  ({defender_id})
Location: K:{defender_k} X:{defender_x} Y:{defender_y}
Bubble Expires in {delta_days} days, {delta_hours} hours, {delta_minutes} minutes.
Expiration time: {datetime.utcfromtimestamp(shield_ts_value)} UTC
"""
    result_message += "\n--Unable to Delete from Defender's Journal"
    try:
        delete_journal_entry(str(defender_id), int(entry_id))
        result_message += "\n--Deleted Successfully from Defender's Journal"
    finally:
        return result_message


def format_caravan(journal_entry: Union[int, dict], csv_output=False) -> str:
    result_message = ""
    player_mgr = PlayerIdManager()

    if isinstance(journal_entry, int):
        journal_result = get_journal_data_by_id(journal_entry)

    elif isinstance(journal_entry, dict):
        journal_result = journal_entry
    else:
        raise TypeError("Dict or Int Expected")

    journal_entry_id = _get_journal_id_from_journal_result(journal_result)
    entry_ts = _get_journal_ts_from_journal_result(journal_result)
    data = journal_result.get('result', {}).get("entries", [{}])[0].get("data", {})
    if not data:
        return "Error Parsing Caravan"

    stuff = data.get('stuff', {}).get('items', {})
    sender = data.get("sender", [])
    receiver = data.get("receiver", [])
    receiver_location = data.get("receiverCoord", {"x": 0, "y": 0, "realId": 0})
    success = data.get("success", False)

    if not success:
        return "Caravan Failed"

    if stuff and sender and receiver:
        stuff_item = int(list(stuff.keys())[0])
        stuff_item_name = itemids.get(stuff_item, f'Unknown item {stuff_item}')
        stuff_count = stuff[str(stuff_item)]

        sender_kingdom = sender[0]
        sender_id = sender[1]
        receiver_kingdom = receiver[0]
        receiver_id = receiver[1]
        sender_name = player_mgr.get_player_by_id(player_mgr.encode_user_id(sender_kingdom, sender_id))
        receiver_name = player_mgr.get_player_by_id(player_mgr.encode_user_id(receiver_kingdom, receiver_id))
        receiver_static_id = data.get("receiverStaticId", 0)

        receiver_extra = ""
        if receiver_static_id not in [2, 4]:
            receiver_extra = f"ID: {receiver_static_id}"
        elif receiver_static_id == 2:
            receiver_extra = "(City)"
        elif receiver_static_id == 4:
            receiver_extra = "(Portal)"

        if csv_output:
            result_message = f"{journal_entry_id},{entry_ts},C,{sender_name.clan_id},{sender_name.name}," + \
                             f"{receiver_name.clan_id}," + \
                             f"{receiver_name.name},{stuff_item_name},{stuff_count}\n"
        else:
            result_message = \
                f"""
Caravan Entry
Sender: [{sender_name.clan_id}] {sender_name.name} ({player_mgr.encode_user_id(sender_kingdom, sender_id)})
Receiver: [{receiver_name.clan_id}] {receiver_name.name} ({player_mgr.encode_user_id(receiver_kingdom, receiver_id)}) @ ({receiver_extra} at K: {receiver_location['realmId']} X: {receiver_location['x']} Y: {receiver_location['y']})
Sent: {stuff_count} {stuff_item_name}
"""

    return result_message


ANNOUNCEMENT_ENTRY = "announceement"
CLAN_ANNOUNCEMENT_ENTRY = "clan_announcement"
BATTLE_ENTRY = "battle"
BATTLE_NO_MONSTERS = "battle_no_monsters"
PORTAL_BATTLE_ENTRY = "portal_battle"
SCOUT_ENTRY = "scout"
BATTLE_SHIELDED_ENTRY = "battle_shielded"
CARAVAN_ENTRY = "caravan"
TREASURY_BUY = "treasury_buy"
CLAN_KICK = "clan_kick"
CLAN_JOIN = "clan_join"
CLAN_EXIT = "clan_exit"
CRYPT_EVENT = "skelp"

journal_handlers = {
    ANNOUNCEMENT_ENTRY: format_clan_announcement,
    CLAN_ANNOUNCEMENT_ENTRY: format_clan_announcement,
    BATTLE_ENTRY: format_scout_or_attack_journal,
    BATTLE_NO_MONSTERS: format_scout_or_attack_journal,
    PORTAL_BATTLE_ENTRY: format_scout_or_attack_journal,
    SCOUT_ENTRY: format_scout_or_attack_journal,
    BATTLE_SHIELDED_ENTRY: format_bubble_battle,
    CARAVAN_ENTRY: format_caravan,
    CLAN_EXIT: format_clan_event,
    CLAN_JOIN: format_clan_event,
    CLAN_KICK: format_clan_event,
    CRYPT_EVENT: format_crypt_event
}


def _get_journal_id_from_journal_result(journal_result: dict) -> Union[int, None]:
    return journal_result.get("result",
                              {'entries': [{}]}).get("entries", [{}])[0].get("entry_id", None)


def _get_journal_ts_from_journal_result(journal_result: dict) -> Union[int, None]:
    return journal_result.get("result",
                              {'entries': [{}]}).get("entries", [{}])[0].get("entry_ts", None)


def format_default_journal(journal_entry: Union[int, dict]):
    if isinstance(journal_entry, int):
        journal_result = get_journal_data_by_id(journal_entry)

    elif isinstance(journal_entry, dict):
        journal_result = journal_entry
    else:
        raise TypeError("Dict or Int Expected")

    event_name = journal_result.get("result", {'entries': [{}]}).get("entries", [{}])[0].get("data", {}).get(
        "eventName", None)
    _journal_id = _get_journal_id_from_journal_result(journal_result)

    if event_name and _journal_id:
        result_message = f"Journal Entry: {_journal_id} Unknown Event Type: {event_name}"
    else:
        result_message = f"Unknown Journal Entry"
    return result_message


def _filter_journal_kwargs(func, kwargs):
    signature = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in signature.parameters}


def format_journal(*args, **kwargs) -> str:
    response = "-E-"
    if args and isinstance(args[0], int):
        print("Journal Args Passed")
        _journal_id: int = args[0]
    elif kwargs and kwargs.get('journal_entry', None):
        _journal_id: int = kwargs['journal_entry']
    else:
        return "Invalid Arguments passed to format_journal"

    j_response = get_journal_data_by_id(_journal_id)
    if not j_response.get('result', {'entries': []}).get('entries', []):
        print(f"No Journal Found - {_journal_id} - {json.dumps(j_response,indent=4)}")
        return "No Journal Entry Found"

    event_name = _journal_get_entry_type(j_response)
    if event_name:
        handler = journal_handlers.get(event_name, format_default_journal)
        print(f"Calling handler for f{event_name}")
        if kwargs:
            kwargs = _filter_journal_kwargs(handler, kwargs)
        response = handler(*args, **kwargs)
        print(f"Response Length: {len(response)}")
    return response


def _journal_get_entry_type(j_response):
    event_name = j_response.get("result", {'entries': [{}]}).get("entries", [{}])[0].get("data", {}).get("eventName",
                                                                                                         None)
    return event_name


def _transact_journal(payload):
    response = None
    # Define the URL and headers
    tries = 3
    url = "https://game-journal-us-1.totalbattle.com/journal"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69",
        "authority": "game-journal-us-1.totalbattle.com",
        "method": "POST",
        "path": "/journal",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }
    # Define the body data
    data = payload

    # Make the POST request
    while tries:
        try:
            response = requests.post(url, headers=headers, json=data)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            tries -= 1

    if response:
        return response.json()
    else:
        return {}


def delete_journal_entry(player_id: str, j_id: int):
    pm = PlayerIdManager()

    player_spawn_kingdom, player_spawn_id = pm.decode_user_id(player_id)
    # Define the request payload
    payload = {
        "jsonrpc": "2.0",
        "method": "Jrn.SetFlags",
        "params": [
            {
                "guid": [player_spawn_kingdom, player_spawn_id],
                "flags": [{"entry_id": j_id, "flag": 3}]
            }
        ]
    }
    return _transact_journal(payload)


def get_journal_data_by_id(j_id):
    # Daanil on 87.
    sacrificial_player = [87, 362121]
    data = {
        "jsonrpc": "2.0",
        "method": "Jrn.GetData",
        "params": [{"guid": sacrificial_player, "entry_ids": [j_id]}]
    }

    return _transact_journal(data)


def get_journal_entry_ids(user_guid: Union[str, list], current_max=0, current_min=0, include_deleted=False,
                          include_starred=False):
    # URL

    include_mask = 6553600

    if include_starred and include_deleted:
        return "may not include both deleted and starred entries.  Submit the query one at a time."
    if include_deleted:
        include_mask += 3
    if include_starred:
        include_mask += 4

    if isinstance(user_guid, list):
        _user_guid_kingdom: int = user_guid[0]
        _user_guid_id: int = user_guid[1]
    elif isinstance(user_guid, str):
        player_mgr = PlayerIdManager()
        _user_guid_kingdom, _user_guid_id = player_mgr.decode_user_id(user_guid)
    else:
        raise TypeError("user_guid should be string or list of integers")

    print(f"Getting List of Entries for {_user_guid_kingdom}:{_user_guid_id} max: {current_max}"
          f"min: {current_min} deleted: {include_deleted} saved: {include_starred}")

    url = "https://game-journal-us-1.totalbattle.com/journal"
    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36",
        "authority": "game-journal-us-1.totalbattle.com",
        "method": "POST",
        "path": "/journal",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "sec-ch-ua": '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    # JSON Body
    data = {
        "jsonrpc": "2.0",
        "method": "Jrn.GetEntries",
        "deviceIdentifier": "fpc64a0816d6c2f41.38696258",
        "params": [{
            "guid": [_user_guid_kingdom, _user_guid_id],
            "min_num": current_min,
            "max_num": current_max,
            "exclude_flags": 0,
            "include_flags": include_mask
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


if __name__ == "__main__":
    json_response = get_journal_data_by_id(int(sys.argv[1]))
    print(json.dumps(json_response, indent=4))


def timestamp_n_days_ago(n):
    # Calculate the date N days ago
    date_n_days_ago = datetime.utcnow() - timedelta(days=n)

    # Create a new datetime object for one minute past midnight of the date N days ago
    one_minute_past_midnight = datetime(date_n_days_ago.year,
                                        date_n_days_ago.month,
                                        date_n_days_ago.day,
                                        0,
                                        0)

    # Convert the datetime object to a UNIX timestamp
    timestamp = int(time.mktime(one_minute_past_midnight.timetuple()))

    return timestamp


if __name__ == '__main__':
    journal_id = int(sys.argv[1])
    filename = sys.argv[2]

    j_entry = get_journal_data_by_id(journal_id)
    open(filename, "w").write(json.dumps(j_entry, indent=4))
