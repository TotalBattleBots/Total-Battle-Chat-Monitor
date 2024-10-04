import json
import sys
import getopt
import jsonpickle
import os
import datetime

c_dict = {}

chat_save_file = "chat_list_data.json"
exclude_name = 'Varys'


def save_state():
    open(chat_save_file, "w").write(jsonpickle.dumps(c_dict))


def load_state():
    global c_dict
    if os.path.exists(chat_save_file):
        try:
            c_dict = jsonpickle.loads(open(chat_save_file, "r").read())
        except Exception:
            pass


def display_chat(chat):
    output_string = ""
    output_string += "------------------------------------------------------------------------------------\n"
    output_string += f"Name: {chat['channel_name']}\n"
    output_string += f"Channel Path: {chat['channel_url']}\n"
    output_string += f"Created By: {chat['created_by']}\n"
    last_message = chat['last_message']
    if last_message:
        last_message_time = datetime.datetime.utcfromtimestamp(last_message.get('created_at', 0) / 1000)
        output_string += f"Last Message Time: {str(last_message_time)} UTC" + "\n"
        output_string += \
            f'Last Message: {last_message.get("user", {"nickname": "--DELETED USER--"})["nickname"]}' + \
            f' : {last_message["message"]}\n'
    output_string += "Members:\n"
    for member in chat["member_list"]:
        if member['nickname'] == 'Varys':
            continue
        try:
            clan = (member['metadata']['memberInfo'].split(','))[-1]
        except Exception:
            clan = "[]"
        output_string += f"[{clan}] {member['nickname']} : {member['metadata'].get('memberInfo', '')}\n"
    output_string += "\n"
    return output_string


def search_chats(search_nick_name=None, search_clan_name=None, search_channel_name=None):
    load_state()
    results = []
    searched_channels = 0
    for channel, channel_data in c_dict.items():
        searched_channels = searched_channels + 1
        if search_channel_name:
            if search_channel_name in channel_data['channel_name']:
                results.append(channel_data)
        else:
            for member in channel_data['member_list']:
                try:
                    clan = (member['metadata']['memberInfo'].split(','))[-1]
                except Exception:
                    clan = ""

                if search_nick_name and search_nick_name.lower() != member['nickname'].lower():
                    continue

                if search_clan_name and clan != search_clan_name:
                    continue

                results.append(channel_data)
                break

    sorted_results = sorted(results, key=lambda chat: (chat['last_message'] or {}).get('created_at', 0), reverse=True)
    print(f"Searched {searched_channels} channels")
    return results


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:c:t:")
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    search_nick_name = None
    search_clan_name = None
    search_channel_name = None

    for o, a in opts:
        if o == "-n":
            search_nick_name = a
        elif o == "-c":
            search_clan_name = a
        elif o == "-t":
            search_channel_name = a

    if search_nick_name is None and search_clan_name is None and search_channel_name is None:
        print(f"Usage: python {sys.argv[0]} -n <nickname> and/or -c <clan> or -t <substring of channel_name>")
        sys.exit(2)

    results = search_chats(search_nick_name, search_clan_name, search_channel_name)
    for result in results:
        print(display_chat(result))


if __name__ == "__main__":
    main()
