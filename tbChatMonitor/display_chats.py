import datetime
import jsonpickle
import os

c_dict = {}

chat_save_file = "chat_list_data.json"


def save_state():
    open(chat_save_file, "w").write(jsonpickle.dumps(c_dict))


def load_state():
    global c_dict
    if os.path.exists(chat_save_file):
        c_dict = jsonpickle.loads(open(chat_save_file, "r").read())
        print(f"Loaded {len(c_dict)} chats.")


def display_chat(chat):
    print("------------------------------------------------------------------------------------")
    print(f"Name: {chat['channel_name']}")
    print(f"Channel Path: {chat['channel_url']}")
    print(f"Last Seen Time: {datetime.datetime.utcfromtimestamp(chat['last_seen_time'] / 1000)}")
    print(f"Created By: {chat['created_by']}")
    last_message = chat['last_message']
    if last_message:
        last_message_time = datetime.datetime.utcfromtimestamp(last_message.get('created_at', 0) / 1000)
        print(f"Last Message Time: {last_message_time} UTC")
        print(
            f'Last Message: {last_message.get("user", {"nickname": "--DELETED USER--"})["nickname"]} : {last_message["message"]}')
    print("Members:")
    for member in chat["member_list"]:
        clan = (member['metadata']['memberInfo'].split(','))[-1]
        print(f"[{clan}] {member['nickname']}")
    print("\n")


if __name__ == '__main__':

    load_state()
    print(f"Loaded {len(c_dict)} chats.")

    for c_key in c_dict.keys():
        display_chat(c_dict[c_key])
