import requests

# Define the URL, headers, and content type
url = "https://game-db-us-3.totalbattle.com/rubens-realm100"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76",
    "authority": "game-db-us-3.totalbattle.com",
    "method": "POST",
    "path": "/rubens-realm100",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
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
content_type = "application/octet-stream"

# Make the POST request
response = requests.post(url, headers=headers, data=None, stream=True)

# Save the binary response content to a file
output_file_path = "output.bin"
with open(output_file_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"Data saved to {output_file_path}")
