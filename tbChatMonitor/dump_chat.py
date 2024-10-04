import requests
import json
import sys
from urllib import parse
from typing import Dict, List
import datetime
from _group_chats import get_all_group_chat_messages, format_group_message
# Endpoint URL


if __name__ == '__main__':
    messages = get_all_group_chat_messages(sys.argv[1])
    for message in messages:
        print(format_group_message(message))
