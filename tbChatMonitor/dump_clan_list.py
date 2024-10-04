import json
import sys
import traceback

import _tb_message_api
import _clan_chat
import time

GUARDIAN_POINTS_ID = 2083
STACK_MINIMUM = 50000

player_data = {}
attack_metadata = {}
csv_filename_detail = ""
csv_file_summary = ""
terminal_ts = 0



def do_main():

    journal_query_list = {}

    clan_id = (sys.argv[1])
    clan_message_path = f"triumph_clan_channel_{clan_id}"
    output_filename = f"{_clan_chat.credentials[clan_id]['clan_name']}-members_list.csv"
    open(output_filename, "w+", encoding="utf-8").write("name,player_id\n")

    # Get the list of members in the clan.
    member_list = _tb_message_api.list_users_in_chat(clan_message_path,
                                                     session_key=_clan_chat.credentials[clan_id]['session_key'],
                                                     access_token=_clan_chat.credentials[clan_id]['access_token'],
                                                     do_join=False)

    for member in member_list:
        player_id = (member['metadata']['memberInfo'].split(','))[1]
        player_name = member['nickname']
        print(f"{player_name} : {member['metadata']} : {len(player_id)}")
        open(output_filename,"a", encoding='utf-8').write(f"{player_name},{player_id}\n")

from typing import List

if '__main__' == __name__:
    do_main()
