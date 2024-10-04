import requests
import json

# Define the URL, headers, content type, and body
url = "https://game-journal-us-1.totalbattle.com/journal"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76",
    "authority": "game-journal-us-1.totalbattle.com",
    "method": "POST",
    "path": "/journal",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,de;q=0.8",
    "dnt": "1",
    "origin": "https://totalbattle.com",
    "referer": "https://totalbattle.com/",
    "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}
content_type = "application/json"
body = {
    "jsonrpc": "2.0",
    "method": "Jrn.GetEntries",
    "deviceIdentifier": "fpc64a0816d6c2f41.38696258",
    "params": [{
        "guid": [78, 180116],
        "min_num": 0,
        "max_num": 0,
        "exclude_flags": 25,
        "include_flags": 6553600
    }]
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(body), stream=True)

# Print the response (optional)
print(json.dumps(response.json(), indent=4))

