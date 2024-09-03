import requests
from datetime import datetime, timezone

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
        print("Login successful")
        data = response.json()
        return data['accessJwt'], data['did']  # return JWT token and DID
    else:
        print("Login failed")
        print(response.text)
        return None, None

def post_to_bluesky(jwt, did, content):
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json'
    }

    # Get the current time with timezone-aware UTC
    current_time = datetime.now(timezone.utc).isoformat()

    payload = {
        "repo": did,  # your Bluesky repo identifier (DID)
        "collection": "app.bsky.feed.post",  # collection for Bluesky posts
        "record": {
            "text": content,
            "createdAt": current_time  # automatically insert the current time
        }
    }
    
    response = requests.post(f'{BASE_URL}/xrpc/com.atproto.repo.createRecord', headers=headers, json=payload)
    
    if response.status_code == 200:
        print("Post successful")
    else:
        print("Post failed")
        print(response.text)

if __name__ == "__main__":
    jwt, did = login_to_bluesky()
    if jwt and did:
        post_content = "This is a test post on Bluesky"
        post_to_bluesky(jwt, did, post_content)
