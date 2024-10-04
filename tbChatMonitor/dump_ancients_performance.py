import json
import sys
import traceback

import _journal
import _journal_monitor
import _tb_message_api
import _clan_chat
from _journal import BATTLE_ENTRY, _get_highest_unit_type
import time
from threading import Lock
import concurrent.futures

GUARDIAN_POINTS_ID = 2083
STACK_MINIMUM = 50000

player_data = {}
attack_metadata = {}
csv_filename_detail = ""
csv_file_summary = ""
terminal_ts = 0
data_lock = Lock()


def generate_csv(unix_timestamp, journal_id, player_id, player_name, number_of_stacks, damage_done):
    return f"{unix_timestamp},{journal_id},{player_id}, {player_name},{number_of_stacks},{damage_done}\n"


def do_main():
    global csv_filename_detail
    global csv_file_summary
    global attack_metadata
    global terminal_ts

    journal_query_list = {}

    clan_id = (sys.argv[1])
    terminal_ts = _journal_monitor.timestamp_n_days_ago(3)
    csv_filename_detail = f"{_clan_chat.credentials[clan_id]['clan_name']}-ancients-detail.csv"
    csv_file_summary = f"{_clan_chat.credentials[clan_id]['clan_name']}-ancients-summary.csv"
    clan_message_path = f"triumph_clan_channel_{clan_id}"
    open(csv_filename_detail, "w+", encoding="utf-8").write("timestamp,journal_id,player,stacks,guardian_points\r\n")

    # Get the list of members in the clan.
    member_list = _tb_message_api.list_users_in_chat(clan_message_path,
                                                     session_key=_clan_chat.credentials[clan_id]['session_key'],
                                                     access_token=_clan_chat.credentials[clan_id]['access_token'],
                                                     do_join=False)

    for member in member_list:
        player_id = (member['metadata']['memberInfo'].split(','))[1]
        player_name = member['nickname']
        print(f"{player_name} : {member['metadata']} : {len(player_id)}")
        journal_query_list[player_id] = player_name
        if player_id not in attack_metadata.keys():
            attack_metadata[player_id] = {}
            attack_metadata[player_id]['stacks'] = [0, 0, 0, 0]
            attack_metadata[player_id]['points'] = [0, 0, 0, 0]
            attack_metadata[player_id]['units'] = [0, 0, 0]
            attack_metadata[player_id]['name'] = player_name

    # for one_player in journal_query_list.keys():
    #    process_journal_for_player(one_player)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as exec:
        exec.map(process_journal_for_player, journal_query_list.keys())
        # process_journal_for_player(attack_metadata, csv_filename_detail, journal_query_list, one_player, terminal_ts)

    with open(csv_file_summary, "w", encoding='utf-8') as f:
        for name in attack_metadata.keys():
            line = (
                f"{attack_metadata[name]['name']},{attack_metadata[name]['stacks'][3]},{attack_metadata[name]['stacks'][2]},"
                f"{attack_metadata[name]['stacks'][1]},{attack_metadata[name]['stacks'][0]},"
                f"{attack_metadata[name]['points'][3]},{attack_metadata[name]['points'][2]},"
                f"{attack_metadata[name]['points'][1]},{attack_metadata[name]['points'][0]},"
                f"{attack_metadata[name]['units'][0]},{attack_metadata[name]['units'][1]},"
                f"{attack_metadata[name]['units'][2]}\n")
            f.write(line)


def process_journal_for_player(player_id):
    global attack_metadata
    global csv_filename_detail

    try:
        player_name = attack_metadata[player_id]['name']
        print(f"Found Clan member {player_name} - {player_id}.")
        least_entry = 0
        ancient_entries = 0
        entries_count = 0
        try_count = 0
        hidden_processed = False
        process_hidden = False
        process_starred = False
        starred_processed = False
        while True:
            if try_count > 3:
                break

            j_result: dict = _journal.get_journal_entry_ids(player_id, current_max=least_entry,
                                                            include_deleted=process_hidden,
                                                            include_starred=process_starred)
            if not j_result and try_count < 3:
                print(f"no result.  try count {try_count}")
                try_count += 1
                time.sleep(5)
                continue

            entry_list: list[dict] = j_result.get('result', {}).get('entries', [])
            if not entry_list:
                print(f"No entry list for {player_id}: {j_result}")
                try_count += 1
                time.sleep(5)
                continue

            bottom_entry = entry_list[0].get('entry_id', None)

            entry_list.reverse()
            for entry in entry_list:
                entries_count += 1
                entry_data = _journal.get_journal_data_by_id(entry['entry_id'])
                entry_type = _journal._journal_get_entry_type(entry_data)
                if not entry_type:
                    print(json.dumps(entry_data, indent=4))
                if entry_type in [BATTLE_ENTRY]:
                    entry = entry_data["result"]["entries"][0]
                    journal_id = entry["entry_id"]
                    journal_ts = entry["entry_ts"]
                    if int(journal_ts) < terminal_ts:
                        continue

                    defender = entry['data'].get('defAllies', [{}])[0]
                    attacker = entry['data'].get('attackerAllies', [{}])[0]
                    attacker_units = attacker.get('atom', {}).get('units', {})

                    defender_static_id = int(defender.get('atom', {}).get('info', {}).get('staticId', "2"))
                    if 6000 < defender_static_id < 7000:
                        attacker_unit_levels = _get_highest_unit_type(attacker_units)
                        with data_lock:
                            player_units = attack_metadata[player_id]['units']

                        for i in range(0, len(player_units)):
                            if player_units[i] < attacker_unit_levels[i]:
                                player_units[i] = attacker_unit_levels[i]

                        with data_lock:
                            attack_metadata[player_id]['units'] = player_units

                        ancient_entries += 1
                        defender_hero_unit_list: dict = (defender.get('atom', {}).get('units', {}))
                        number_of_stacks = len(defender_hero_unit_list)

                        for stack in defender_hero_unit_list.keys():
                            if defender_hero_unit_list[stack]['count'] < STACK_MINIMUM:
                                number_of_stacks = max(1, number_of_stacks - 1)

                        guardian_points_gained = attacker.get('gained', {}).get('items', {}).get(
                            str(GUARDIAN_POINTS_ID), 0)
                        csv_line = generate_csv(journal_ts, journal_id, player_id, player_name, number_of_stacks,
                                                guardian_points_gained)


                        with data_lock:
                            attack_metadata[player_id]['stacks'][number_of_stacks - 1] += 1
                            attack_metadata[player_id]["points"][number_of_stacks - 1] += guardian_points_gained
                            open(csv_filename_detail, "a", encoding="utf-8").write(csv_line)

            least_entry = bottom_entry - 1
            entry_data = _journal.get_journal_data_by_id(bottom_entry)
            bottom_entry_ts = _journal._get_journal_ts_from_journal_result(entry_data)
            if not bottom_entry_ts or (terminal_ts and bottom_entry_ts < terminal_ts):
                try_count = 0
                print(f"--{bottom_entry_ts} - {terminal_ts} - {hidden_processed} - {starred_processed}")
                break
        print(
            f"Clan member {player_name} - {player_id} - {entries_count} Entries and {ancient_entries} ancient entries.")
    except Exception:
        print(f"Exception handling {player_id}")
        traceback.print_tb()


from typing import List


def compute_ratfuck_quotient(points_list: List[int]) -> int:
    total = sum(points_list)
    last_3 = sum(points_list[1:])
    if not total:
        return 0
    else:
        return int((float(last_3) / float(total)))


if '__main__' == __name__:
    do_main()
