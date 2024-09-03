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
IMAGE_BASE_URL = 'https://f0ck.org/data/posts'
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

# Funktion zum Hochladen einer Mediendatei zu Bluesky
def upload_media(jwt, media_url):
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json'
    }
    
    # Herunterladen der Mediendatei
    media_response = requests.get(media_url)
    if media_response.status_code != 200:
        print(f"Failed to download media from {media_url}")
        return None
    
    media_data = media_response.content
    files = {
        'file': ('mediafile', media_data)
    }
    
    upload_response = requests.post(f'{BASE_URL}/xrpc/com.atproto.repo.uploadBlob', headers=headers, files=files)
    
    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        media_url = upload_data.get('blob', {}).get('url', '')
        print(f"Media upload successful: {media_url}")
        return media_url
    else:
        print("Media upload failed")
        print(upload_response.text)
        return None

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
    
    if media_url:
        # Anhang hinzufügen, wenn vorhanden
        record_payload["record"]["attachments"] = [media_url]
    
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
            file_url = post_data.get('contentUrl', 'No URL')
            comment = post_data.get('comments', [{}])[0].get('text', 'No Comment')
            user = post_data.get('user', {})
            username = user.get('name', 'Anonymous')
            
            # URLs anpassen
            image_url = f"{IMAGE_BASE_URL}/{file_url.split('/')[-1]}"  # Die URL des Bildes
            post_url = f"{POST_BASE_URL}/{post_id}"
            
            # Mediendatei hochladen
            media_url = upload_media(jwt, image_url) if file_url != 'No URL' else None
            
            content = (
                f"📸 New Post by {username}\n"
                f"💬 Comment: {comment}\n\n"
                f"🔗 View Post: {image_url}\n"
                f"🌐 Post URL: {post_url}\n\n"
                f"🌟 Tags: {title}"
            )
            
            post_to_bluesky(jwt, did, content, media_url)
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
