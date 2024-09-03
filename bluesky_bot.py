import requests
from datetime import datetime, timezone
import time

# Deine Bluesky-Anmeldeinformationen
USERNAME = 'your_bluesky_username'
PASSWORD = 'your_bluesky_password'
BASE_URL = 'https://bsky.social'

# API-URL für f0ck.org
SZURU_API_URL = 'https://f0ck.org/api'

# Basis-URL für die Bild- und Post-Links
POST_BASE_URL = 'https://f0ck.org/post'

# Funktion zum Einloggen in Bluesky
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
        return data['accessJwt'], data['did']
    else:
        print("Login failed")
        print(response.text)
        return None, None

# Funktion zum Abrufen eines spezifischen Beitrags von f0ck.org
def fetch_post_from_szurubooru(post_id):
    try:
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(f'{SZURU_API_URL}/post/{post_id}', headers=headers)
        print(f"Fetching post {post_id}: Status {response.status_code}")
        if response.status_code == 200:
            post_data = response.json()
            print(f"Post data: {post_data}")  # Debugging info
            return post_data
        elif response.status_code == 404:
            print(f"Post {post_id} not found. Skipping to the next ID.")
            return None
        else:
            print(f"Failed to fetch post {post_id}. Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching post {post_id}: {e}")
        return None

# Funktion zum Posten auf Bluesky
def post_to_bluesky(jwt, did, content, media_url=None):
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json'
    }

    current_time = datetime.now(timezone.utc).isoformat()

    record_payload = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": content,
            "createdAt": current_time
        }
    }
    
    response = requests.post(f'{BASE_URL}/xrpc/com.atproto.repo.createRecord', headers=headers, json=record_payload)
    
    if response.status_code == 200:
        print("Post successful")
    else:
        print("Post failed")
        print(response.text)

# Hauptschleife zum Abrufen und Posten von Beiträgen
def post_loop():
    jwt, did = login_to_bluesky()
    if not (jwt and did):
        return

    post_id = 1  # Start bei Post-ID 1

    while True:
        post_data = fetch_post_from_szurubooru(post_id)
        
        if post_data:
            title = post_data.get('tags', [{}])[0].get('names', ['No Title'])[0]
            comment = post_data.get('comments', [{}])[0].get('text', 'No Comment')
            user = post_data.get('user', {})
            username = user.get('name', 'Anonymous')
            
            # URLs anpassen
            post_url = f"{POST_BASE_URL}/{post_id}"
            
            content = (
                f"🌐 Post URL: {post_url}\n"
                f"💬 Comment: {comment}\n"
                f"🌟 Tags: {title}\n"
                f"📸 Post by {username}"
            )
            
            post_to_bluesky(jwt, did, content)
            print(f"Posted post ID {post_id} to Bluesky")
            post_id += 1  # Move to the next post ID
            time.sleep(6 * 60 * 60)  # 6 Stunden warten nach einem erfolgreichen Post
        
        else:
            # Warten 1 Sekunde, bevor die nächste ID ausprobiert wird
            print(f"No valid post found at ID {post_id}. Skipping to the next ID.")
            post_id += 1
            time.sleep(1)

if __name__ == "__main__":
    post_loop()
