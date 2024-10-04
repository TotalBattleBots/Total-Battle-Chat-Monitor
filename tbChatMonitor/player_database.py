import json

from _model_user import PlayerIdManager, Player
import jsonpickle
import getopt
import sys
import os
from _kingdom_chat import _kingdom_chat_members
from _clan_chat import _clan_chat_members
from typing import List

print('working')


def load_state(parse_filename):
    c_dict = {}
    if os.path.exists(parse_filename):
        try:
            c_dict = jsonpickle.loads(open(parse_filename, "r").read())
        except Exception:
            pass
    return c_dict


def update_player_database_from_kingdom(kingdom_id):
    member_list = _kingdom_chat_members(kingdom_id)
    if member_list:
        update_player_database_from_member_list(member_list)


def update_player_database_from_clan(clan_id):
    member_list = _clan_chat_members(clan_id)
    if member_list:
        update_player_database_from_member_list(member_list)


def update_player_database_from_file(parse_filename):
    c_dict = load_state(parse_filename)
    for channel, channel_data in c_dict.items():
        member_list = channel_data['member_list']
        update_player_database_from_member_list(member_list)


def update_player_database_from_member_list(member_list: List[dict]):
    manager = PlayerIdManager()
    for member in member_list:
        try:
            clan = (member['metadata']['memberInfo'].split(','))[-1]
            if not clan:
                clan = "   "
            player_id = (member['metadata']['memberInfo'].split(','))[1]
            name = member['nickname']
            chat_user_id = member['user_id']
            manager.add_entry(user_id=player_id, clan_id=clan, name=name, chat_user_id=chat_user_id)
        except KeyError:
            print(f"Keyerror processing {member['nickname']} : {member['metadata']}")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:u:n:g:k:c:", ["help", "parse=", "userid=", "name=",
                                                           "groupid=", "kingdom=", "clan="])
    except getopt.GetoptError:
        print(
            f'{sys.argv[0]}  -c <clan_number> | -k <kingdom> | -p <chat_pickle_file> | -u <user_id> -n <name> -g <group_id>')
        sys.exit(2)

    if not opts:
        print(
            f'{sys.argv[0]}  -c <clan_number> | -k <kingdom> | -p <chat_pickle_file> | -u <user_id> -n <name> -g <group_id>')
        sys.exit(2)

    users = []
    user_id = None
    name = None
    group_id = None
    parse_filename = None
    clan_id = None
    kingdom_id = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('UserManager.py -u <user_id> -n <name> -g <group_id> -k kingdom')
            sys.exit()
        elif opt in ("-u", "--userid"):
            user_id = arg
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-g", "--groupid"):
            group_id = arg
        elif opt in ("-p", "--parse"):
            parse_filename = arg
        elif opt in ('-k', "--kingdom"):
            kingdom_id = arg
        elif opt in ('-c' "--clan"):
            clan_id = arg

    manager = PlayerIdManager()
    if user_id:
        print(display_user(manager.get_player_by_id(user_id=user_id)))
    elif name or group_id:
        for oneuser in manager.query_users(name=name, clan_id=group_id):
            print(display_user(oneuser))
    elif parse_filename:
        update_player_database_from_file(parse_filename=parse_filename)
    elif kingdom_id:
        update_player_database_from_kingdom(kingdom_id)
    elif clan_id:
        update_player_database_from_clan(clan_id)


def display_user(oneuser: Player):
    start_k, player_no = PlayerIdManager.decode_user_id(oneuser.user_id)
    if start_k:
        return f"User ID: [{start_k},{player_no}] ({oneuser.user_id}), Name: {oneuser.name}, Group ID: {oneuser.clan_id}"


if __name__ == "__main__":
    main(sys.argv[1:])
