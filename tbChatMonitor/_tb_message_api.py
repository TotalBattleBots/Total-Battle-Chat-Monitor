import requests
import json
import time
from typing import Dict, List, Optional
from _model_user import PlayerIdManager

# Configuration
APP_ID = "1CA99C8C-22B2-4DE6-9507-052C59BBB504"
SENDBIRD_HOST = f"api-{APP_ID.lower()}.sendbird.com"

CHAT_USER = {
    "session_key": "4514d3658533907e029dcc37a46bd42d170bd4f6",
    "access_token": "1b2050e150e418b0f68c60f027672dc3dc9aa559",
    'user_id': "site2:6406668",
    'kingdom': 'K70',
    'email': 'tim.lawless+k70.1@gmail.com',
}

# Lance Announcements
test_chat = "sendbird_group_channel_114122295_1e09fe015cab58128a85a258fc395880191869ad"


def generate_headers(method: str, session_key: str, path: str = None, access_token: str = None) -> Dict[str, str]:
    time_now = int(time.time() * 1000)
    headers = {
        "User-Agent": "Mozilla/5.0 ...",
        "authority": SENDBIRD_HOST,
        "method": method,
        "path": path,
        "scheme": "https",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "accept": "*/*",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sb-user-agent": "JS%2Fc4.2.3%2F%2F%2F",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML. like Gecko) "
                    "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188,4.2.3,"
                    f"{APP_ID}",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "session-key": session_key,
    }

    if access_token:
        headers["access-token"] = access_token

    if path:
        headers["path"] = path

    return headers


def list_users_in_chat(chat_url: str,
                       session_key: str = CHAT_USER['session_key'],
                       access_token: str = CHAT_USER['access_token'],
                       user_id: str = CHAT_USER['user_id'],
                       do_join: bool = True):
    time_now = int(time.time() * 1000)
    member_list = []

    if do_join and not join_chat(chat_path=chat_url, session_key=session_key, access_token=access_token,
                                 user_id=user_id):
        return member_list

    next_token = ""

    try:
        while True:
            path = f"/v3/group_channels/{chat_url}/members?token={next_token}&limit=100&order" \
                   f"=operator_then_member_alphabetical&muted_member_filter=all&member_state_filter=all&operator_filter=all" \
                   f"&show_member_is_muted=true&show_read_receipt=true&show_delivery_receipt=true"
            url = f"https://{SENDBIRD_HOST}{path}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
                "authority": f"{SENDBIRD_HOST}",
                "method": "PUT",
                "path": path,
                "app-id": f"{APP_ID}",
                "scheme": "https",
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-US,en;q=0.9,de;q=0.8",
                "dnt": "1",
                "origin": "https://totalbattle.com",
                "referer": "https://totalbattle.com/",
                "request-sent-timestamp": f"{time_now}",
                "sb-user-agent": "JS%2Fc4.2.3%2F%2F%2F",
                "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML. like Gecko) "
                            f"Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54,4.2.3,{APP_ID}",
                "session-key": f"{session_key}",
                "access-token": f"{access_token}"
            }

            print(f"Requesting Members. Next Token: {next_token}: {path}")
            response = requests.get(url, headers=headers)
            data = response.json()

            next_token = data.get("next", "")
            try:
                member_list = member_list + data["members"]
            except KeyError as e:
                print(json.dumps(data, indent=4))
            if not next_token or next_token == "":
                break
    finally:
        if do_join:
            leave_chat(chat_path=chat_url, session_key=session_key, access_token=access_token)

    return member_list


def join_chat(chat_path: str,
              session_key: str = CHAT_USER['session_key'],
              access_token: str = CHAT_USER['access_token'],
              user_id: str = CHAT_USER['user_id']) -> bool:
    """

    :param chat_path:
    :param session_key:
    :param access_token:
    :param user_id:
    :return:
    """

    time_now = int(time.time() * 1000)

    url = f"https://{SENDBIRD_HOST}/v3/group_channels/{chat_path}/join"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "authority": f"{SENDBIRD_HOST}",
        "method": "PUT",
        "path": f"/v3/group_channels/{chat_path}/join",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sb-user-agent": "JS%2Fc4.2.3%2F%2F%2F",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML. like Gecko) "
                    f"Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54,4.2.3,{APP_ID}",
        "session-key": f"{session_key}",
        "access-token": f"{access_token}"
    }

    data = {
        "user_id": f"{user_id}"
    }

    response = requests.put(url, headers=headers, json=data)

    # Check if request was successful
    if response.status_code == 200:
        print("Request was successful!")
        return True
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
        return False


def leave_chat(chat_path: str,
               user_id: str = CHAT_USER['user_id'],
               session_key: str = CHAT_USER['session_key'],
               access_token: str = CHAT_USER['access_token']) -> bool:
    """

    :param user_id:
    :param chat_path:
    :param session_key:
    :param access_token:
    :return:
    """
    time_now = time.time()

    url = f"https://{SENDBIRD_HOST}/v3/group_channels/{chat_path}/leave"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "authority": f"{SENDBIRD_HOST}",
        "method": "PUT",
        "path": f"/v3/group_channels/{chat_path}/leave",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/539.36 (KHTML. like Gecko) "
                    f"Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1948.54,4.2.3,{APP_ID}",
        "session-key": f"{session_key}",
        "access-token": f"{access_token}"
    }

    data = {
        "user_id": f"{user_id}",
        "should_remove_operator_status": False
    }

    response = requests.put(url, headers=headers, json=data)

    # Check if request was successful
    if response.status_code == 200:
        print("Request was successful!")
        return True
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
        return False

def ban_from_chat(chat_path: str,
                  ban_user_id: str,
                  session_key: str,
                  access_token: str,
                  ban_time=(60 * 60 * 24 * 7)) -> dict:
    """

    :param do_join:
    :param user_id:
    :param chat_path:
    :param session_key:
    :param access_token:
    :param ban_user_id:
    :param ban_time:
    :return:
    """
    time_now = int(time.time() * 1000)
    pm = PlayerIdManager()
    user_info = pm.get_player_by_id(ban_user_id)
    response_json = {}
    if user_info.name == "UNK":
        print(f"Unable to find invitee by id {ban_user_id}")
        return response_json

    invited_user_chat_id = user_info.chat_user_id
    url = f"https://{SENDBIRD_HOST}/v3/group_channels/{chat_path}/ban"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "authority": f"{SENDBIRD_HOST}",
        "method": "PUT",
        "path": f"/v3/group_channels/{chat_path}/ban",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/539.36 (KHTML. like Gecko) "
                    f"Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1948.54,4.2.3,{APP_ID}",
        "session-key": f"{session_key}",
        "access-token": f"{access_token}"
    }

    data = {
        "user_id": invited_user_chat_id,
        "seconds": ban_time,
        "description": ""
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.text)
    finally:
        pass

    return response_json

def unban_from_chat(chat_path: str,
                  ban_user_id: str,
                  session_key: str,
                  access_token: str) -> dict:
    """

    :param do_join:
    :param user_id:
    :param chat_path:
    :param session_key:
    :param access_token:
    :param ban_user_id:
    :param ban_time:
    :return:
    """
    time_now = int(time.time() * 1000)
    pm = PlayerIdManager()
    user_info = pm.get_player_by_id(ban_user_id)
    response_json = {}
    if user_info.name == "UNK":
        print(f"Unable to find invitee by id {ban_user_id}")
        return response_json

    banned_user_chat_id = user_info.chat_user_id
    url = f"https://{SENDBIRD_HOST}/v3/group_channels/{chat_path}/unban/{banned_user_chat_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "authority": f"{SENDBIRD_HOST}",
        "method": "DELETE",
        "path": f"/v3/group_channels/{chat_path}/unban/{banned_user_chat_id}",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/539.36 (KHTML. like Gecko) "
                    f"Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1948.54,4.2.3,{APP_ID}",
        "session-key": f"{session_key}",
        "access-token": f"{access_token}"
    }

    try:
        response = requests.delete(url, headers=headers)
    finally:
        pass

    return response_json



def invite_to_chat(chat_path: str,
                   invitee_id: str,
                   session_key: str = CHAT_USER['session_key'],
                   access_token: str = CHAT_USER['access_token'],
                   user_id: str = CHAT_USER['user_id'],
                   do_join: bool = True) -> bool:
    """

    :param do_join:
    :param user_id:
    :param chat_path:
    :param invitee_id:
    :param session_key:
    :param access_token:
    :return:
    """
    time_now = int(time.time() * 1000)
    pm = PlayerIdManager()
    user_info = pm.get_player_by_id(invitee_id)
    response_json = {}
    if user_info.name == "UNK":
        print(f"Unable to find invitee by id {invitee_id}")
        return response_json

    invited_user_chat_id = user_info.chat_user_id
    url = f"https://{SENDBIRD_HOST}/v3/group_channels/{chat_path}/invite"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "authority": f"{SENDBIRD_HOST}",
        "method": "PUT",
        "path": f"/v3/group_channels/{chat_path}/invite",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/539.36 (KHTML. like Gecko) "
                    f"Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1948.54,4.2.3,{APP_ID}",
        "session-key": f"{session_key}",
        "access-token": f"{access_token}"
    }

    data = {
        "user_ids": [invited_user_chat_id]
    }

    if do_join and not join_chat(chat_path=chat_path, session_key=session_key,
                                 access_token=access_token, user_id=user_id):
        print(f"Failed to join chat path {chat_path}")
        return response_json

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
    finally:
        if do_join:
            leave_chat(chat_path=chat_path, user_id=user_id, session_key=session_key, access_token=access_token)

    return response_json

def get_tb_messages(message_path: str,
                    session_key: str = CHAT_USER['session_key'],
                    access_token: str = CHAT_USER['access_token'],
                    time_stamp: int = 9007199254740991) -> Dict:
    """

    :param time_stamp:
    :param message_path:
    :param session_key:
    :param access_token:
    :param dump_all_messages:
    :return:
    """

    time_now = int(time.time() * 1000)

    path = f"{message_path}/messages?is_sdk=true&prev_limit=20&next_limit=0&include=false" \
           f"&reverse=true&message_ts={time_stamp}&message_type=&include_reply_type=none&with_sorted_meta_array=false" \
           f"&include_reactions=false&include_thread_info=false&include_parent_message_info=false" \
           f"&show_subchannel_message_only=false&include_poll_details=true",

    url = f"https://{SENDBIRD_HOST}{path[0]}"

    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
        "authority": f"{SENDBIRD_HOST}",
        "method": "GET",
        "path": f"{path[0]}",

        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de;q=0.8",
        "access-token": f"{access_token}",
        "app-id": f"{APP_ID}",
        "dnt": "1",
        "origin": "https://totalbattle.com",
        "referer": "https://totalbattle.com/",
        "request-sent-timestamp": f"{time_now}",
        "sb-user-agent": "JS%2Fc4.2.3%2F%2F%2F",
        "sec-ch-ua": '''Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"''',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML. like Gecko) "
                    "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203,4.2.3,1CA99C8C-22B2-4DE6-9507-052C59BBB504",
        "session-key": f"{session_key}"
    }
    # Make the GET request
    response = requests.get(url, headers=headers)
    return json.loads(response.text)
