import requests
import sys

# Set the base URL for the SendBird API
base_url = "https://api-1ca99c8c-22b2-4de6-9507-052c59bbb504.sendbird.com/v3"

# Set the group channel URL
channel_url = "sendbird_group_channel_114158915_eae44bd60a4663e20dc891a79cae478bb607ecfa"

# Set the message ID to delete
message_id = 6444040387 

# Set the headers, including the access token for authentication
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "session-key": "ef241fff67934614eeb08e22a9468d47ca60d2d3",
    "access-token": "716e5b62b1c77bf994a259a04dd9d5d413b809de",
    "app-id": "1CA99C8C-22B2-4DE6-9507-052C59BBB504",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,de;q=0.8",

}

# Make the DELETE request to the appropriate endpoint
response = requests.delete(
    f"{base_url}/group_channels/{channel_url}/messages/{message_id}",
    headers=headers
)

# Print the response
if response.status_code == 200:
    print("Message deleted successfully.")
else:
    print(f"Failed to delete the message: {response.status_code}, {response.text}")

