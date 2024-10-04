from _journal import format_journal, get_journal_data_by_id, get_journal_entry_ids
from _journal import BATTLE_ENTRY, BATTLE_SHIELDED_ENTRY, PORTAL_BATTLE_ENTRY, BATTLE_NO_MONSTERS
from _journal import CLAN_ANNOUNCEMENT_ENTRY, ANNOUNCEMENT_ENTRY, SCOUT_ENTRY, CARAVAN_ENTRY, CRYPT_EVENT
from _journal import _journal_get_entry_type, timestamp_n_days_ago, _get_journal_ts_from_journal_result
import pickle
import time
import datetime
import discord
import random
from _journal import delete_journal_entry
current_state = {}
that_guy_id = "4f0002d5d4"


def fuck_that_guys_journal(player_id: str = that_guy_id):

    while True:
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
                print(delete_journal_entry(that_guy_id,entry_id))
                top_journal_id = entry_id

            current_state[player_id] = top_journal_id + 1
    time.sleep(1)


if '__main__' == __name__:
    fuck_that_guys_journal()
