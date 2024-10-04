import requests
import json
import sys
from urllib import parse
from typing import Dict, List


# Endpoint URL


def list_chats(keyword: str,
               session_id: str = "42f9d5c77baf6663762ab3211e208ce322d56e49") -> List[Dict]:
    """

    :param keyword:
    :param session_id:
    :return:
    """

    next_token = ""
    safe_keyword = parse.quote(keyword)
    channel_list = []

    while True:
        url = f"https://api-1ca99c8c-22b2-4de6-9507-052c59bbb504.sendbird.com/v3/group_channels?token={next_token}" \
              f"&limit=100&orderchronological&show_member=true&show_read_receipt=true&show_delivery_receipt=true&" \
              f"show_empty=true&public_mode=public&public_membership_mode=all&name_contains={safe_keyword}&" \
              f"super_mode=all&show_frozen=true&show_metadata=true"

        # Custom headers
        headers = {"authority": "api-1ca99c8c-22b2-4de6-9507-052c59bbb504.sendbird.com",
                   "method": "GET",
                   "scheme": "https",
                   "accept": "*/*",
                   "accept-encoding": "gzip, deflate, br",
                   "accept-language": "en-US,en;q=0.9,de;q=0.8",
                   "dnt": "1",
                   "origin": "https://totalbattle.com",
                   "referer": "https://totalbattle.com/",
                   "sb-user-agent": "JS%2Fc4.2.3%2F%2F%2F",
                   "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
                   "sec-ch-ua-mobile": "?0",
                   "sec-ch-ua-platform": '"Windows"',
                   "sec-fetch-dest": "empty",
                   "sec-fetch-mode": "cors",
                   "sec-fetch-site": "cross-site",
                   "sendbird": "JS,Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML. like Gecko) "
                               "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188,4.2.3,"
                               "1CA99C8C-22B2-4DE6-9507-052C59BAAAB01",
                   "session-key": session_id,
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"}

        # Send GET request
        print(f"{url}")
        response = requests.get(url, headers=headers)
        # Get response content
        data = response.json()
        next_token = data.get("next","")
        _channels = data.get("channels", [])
        channel_list = channel_list + _channels

        if not next_token or next_token == "":
            break

    print(f"List channels with pattern of {keyword} returned {len(channel_list)} ")
    return channel_list


if __name__ == '__main__':
    channels = list_chats(sys.argv[1])

    if not channels:
        pass
    else:
        for channel in channels:
            print(json.dumps(channel, indent=4))
            if not channel:
                continue
            print(f'Name: {channel.get("name", "---NONAME---")}')
            try:
                created_by = channel.get("created_by", {
                    "nickname": "--DELETED USER--"
                }).get("nickname", "--DELETED USER--")
            except Exception:
                created_by = "---DELETED-USER---"

            print(f'Created By: {created_by}')
            member_list = [member for member in channel["members"]]
            last_message = channel.get("last_message", None)
            if last_message:
                print(
                    f'Last Message: {last_message.get("user", {"nickname": "--DELETED USER--"})["nickname"]} : {last_message["message"]}'
                )
            print("Members:")
            for member in member_list:
                clan = (member['metadata']['memberInfo'].split(','))[-1]
                print(f"[{clan}] {member['nickname']}")
            print("\n\n")
