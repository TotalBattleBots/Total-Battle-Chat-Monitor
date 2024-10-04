import requests

# Sendbird API endpoint
application_id = '1ca99c8c-22b2-4de6-9507-052c59bbb504'
BASE_URL = f'https://api-{application_id}.sendbird.com/v3'
SESSION_ID = 'c56a74e98cfd0f4aa49a37e0f34eb0f39d74f762'  # Replace with your session ID
ACCESS_TOKEN = 'fd5ac706f5669ce677ccb636371392991b0718d4'  # Replace with your access token
HEADERS = {
    'Content-Type': 'application/json',
    'Session-Key': SESSION_ID,
    'Access-Token': ACCESS_TOKEN
}
CHANNEL_TYPE = "group_channels"  # or 'open_channels'
CHANNEL_URL = "sendbird_group_channel_204854630_03aa7a48dc4d51cad795e2d1b2c1ecc33e31d845"
USER_ID = "site2:5614142"


def send_message(channel_url, user_id, message='/%0%/', subs=None):
    """
    Send a message to a Sendbird channel.

    Args:
    - channel_type (str): Type of the channel ('group_channels' or 'open_channels')
    - channel_url (str): URL of the channel
    - user_id (str): ID of the user sending the message
    - message (str): Message content

    Returns:
    - Response object
    """

    endpoint = f"{BASE_URL}/{CHANNEL_TYPE}/{channel_url}/messages"
    payload = {
        "message_type": "MESG",
        "user_id": user_id,
        "message": message
    }

    if subs:
        payload["data"] = subs


    resp = requests.post(endpoint, headers=HEADERS, json=payload)
    return resp.json()


def send_epic_link(subs: str):
    """
    Send a message to a Sendbird channel.

    Args:
    - channel_type (str): Type of the channel ('group_channels' or 'open_channels')
    - channel_url (str): URL of the channel
    - user_id (str): ID of the user sending the message
    - message (str): Message content

    Returns:
    - Response object
    """

    resp = send_message(channel_url=CHANNEL_URL,
                        user_id=USER_ID,
                        subs=subs)
    print(resp)
    return resp


if __name__ == "__main__":
    response = send_epic_link(subs=r'{"subs":{"/%0%/":{"type":"coord","entryType":"poi","x":573,"y":527,"realmId":100,'
                                   '"staticId":4007,"name":"Epic Inferno squad","v":1}}}')
    print(response)
