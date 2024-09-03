import requests
from datetime import datetime

USERNAME = 'your_bluesky_username'
PASSWORD = 'your_bluesky_password'
BASE_URL = 'https://bsky.social'

def login_to_bluesky():
    session = requests.Session()
    login_payload = {
        'identifier': USERNAME,
        'password': PASSWORD
    }
    response = session.post(f'{BASE_URL}/xrpc/com.atproto.server.createSession', json=login_payload)
    
    if response.status_code == 200:
        print("login succeeded")
        data = response.json()
        return data['accessJwt'], data['did']
    else:
        print("login failed")
        print(response.text)
        return None, None

def post_to_bluesky(jwt, did, content):
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json'
    }

    # Get the current time in the required format (ISO 8601)
    current_time = datetime.utcnow().isoformat() + 'Z'

    payload = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": content,
            "createdAt": current_time  # automatically insert current time
        }
    }
    
    response = requests.post(f'{BASE_URL}/xrpc/com.atproto.repo.createRecord', headers=headers, json=payload)
    
    if response.status_code == 200:
        print("post succeeded")
    else:
        print("error while posting")
        print(response.text)

if __name__ == "__main__":
    jwt, did = login_to_bluesky()
    if jwt and did:
        post_content = "Testpost by the f0ck.org bot"
        post_to_bluesky(jwt, did, post_content)
