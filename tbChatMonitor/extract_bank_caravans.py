from _journal import format_journal, _journal_get_entry_type, get_journal_entry_ids, get_journal_data_by_id
from _journal import CARAVAN_ENTRY, _get_journal_ts_from_journal_result
from _journal import PORTAL_BATTLE_ENTRY, BATTLE_ENTRY
from _journal import timestamp_n_days_ago
from player_database import PlayerIdManager
import sys

# Bank Player IDs:
# Sun Tzu - 4d0000a1bc
# Medici II - 630002a682
DISCORD_BOT_CHANNEL_ID = 1140720607915429998


def get_caravans_xls(player_id: str, days: int):
    if days > 14:
        return "Days exceeds 2 weeks (14 days)"

    least_entry = 0
    terminal_ts = timestamp_n_days_ago(days)
    csv_message = "record_id,unix_ts,record_type,sender_clan,sender_name," + \
                  "receiver_clan,receiver_name,resource_type,amount\r\n"

    while True:
        j_result: dict = get_journal_entry_ids(player_id, current_max=least_entry)
        if not j_result:
            break

        entry_list: list[dict] = j_result.get('result', {}).get('entries', [])
        if not entry_list:
            print(f"No entry list for {player_id}")
            break

        bottom_entry = entry_list[0].get('entry_id', None)

        entry_list.reverse()
        for entry in entry_list:
            entry_id = entry['entry_id']
            entry_data = get_journal_data_by_id(entry['entry_id'])
            entry_type = _journal_get_entry_type(entry_data)
            if entry_type in [CARAVAN_ENTRY, PORTAL_BATTLE_ENTRY, BATTLE_ENTRY]:
                csv_message += format_journal(journal_entry=entry_id, csv_output=True)

        least_entry = bottom_entry - 1
        entry_data = get_journal_data_by_id(bottom_entry)
        bottom_entry_ts = _get_journal_ts_from_journal_result(entry_data)
        print(f"bottom_entry_ts: {bottom_entry_ts} terminal_ts: {terminal_ts}")
        if not bottom_entry_ts or bottom_entry_ts < terminal_ts:
            break

    return csv_message


import sys

if '__main__' == __name__:
    pm = PlayerIdManager()
    bank_info = pm.get_player_by_id(sys.argv[1])

    caravan_data = get_caravans_xls(sys.argv[1], 7)
    open(f"{bank_info.name}-{sys.argv[1]}.csv", mode='w', encoding='utf-8').write(caravan_data)
