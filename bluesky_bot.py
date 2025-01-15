import requests
from datetime import datetime, timezone
import time

# Bluesky login data

USERNAME = 'your_username'
PASSWORD = 'your_password'
BASE_URL = 'https://bsky.social'

# API URL of your instance
SZURU_API_URL = 'https://yoururl.com/api'

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

def fetch_post_from_szurubooru(post_id):
    try:
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(f'{SZURU_API_URL}/post/{post_id}', headers=headers)
        print(f"Fetching post {post_id}: status {response.status_code}")
        if response.status_code == 200:
            post_data = response.json()
            print(f"Post data: {post_data}")  # debugging info
            return post_data
        elif response.status_code == 404:
            print(f"Post {post_id} not found. Skipping to the next id.")
            return None
        else:
            print(f"Failed to fetch post {post_id}. Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching post {post_id}: {e}")
        return None

def upload_image(jwt, image_url):
    try:
        # Download the image
        img_response = requests.get(image_url)
        if img_response.status_code != 200:
            return None

        # Determine mime type
        mime_type = img_response.headers.get('Content-Type', 'image/jpeg')  # default to 'image/jpeg'

        # Upload image to Bluesky
        headers = {
            'Authorization': f'Bearer {jwt}',
            'Content-Type': mime_type
        }
        
        upload_response = requests.post(
            f'{BASE_URL}/xrpc/com.atproto.repo.uploadBlob',
            headers=headers,
            data=img_response.content
        )
        
        if upload_response.status_code == 200:
            return upload_response.json().get('blob')
        return None
    except Exception as e:
        print(f"Error during image upload: {e}")
        return None

def post_to_bluesky(jwt, did, content, image_url=None):
    headers = {
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json'
    }

    current_time = datetime.now(timezone.utc).isoformat()
    
    record = {
        "$type": "app.bsky.feed.post",
        "text": content,
        "createdAt": current_time,
    }
    
    # If an image is provided, add it to the post
    if image_url:
        blob = upload_image(jwt, image_url)
        if blob:
            record["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": [{
                    "alt": "post thumbnail",
                    "image": blob
                }]
            }

    record_payload = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": record
    }
    
    response = requests.post(f'{BASE_URL}/xrpc/com.atproto.repo.createRecord', headers=headers, json=record_payload)
    
    if response.status_code == 200:
        print("Post successful")
        post_response = response.json()
        return post_response.get('uri')
    else:
        print("Post failed")
        print(response.text)
        return None

def post_loop():
    jwt, did = login_to_bluesky()
    if not (jwt and did):
        return

    post_id = 1  # Start with post ID 1

    while True:
        post_data = fetch_post_from_szurubooru(post_id)
        
        if post_data:
            try:
                user = post_data.get('user', {})
                username = user.get('name', 'anonymous') if user else 'anonymous'
            except:
                username = 'anonymous'
            
            # Format URLs with https:// for clickable links
            post_url = f"{SZURU_API_URL}/post/{post_id}"
            # Direct media URL instead of thumbnail
            media_url = f"{SZURU_API_URL}/data/posts/{post_data['contentUrl']}"
            
            # Ensure tags start with '#'
            tags = [f"#{tag['names'][0]}" if not tag['names'][0].startswith('#') else tag['names'][0] for tag in post_data.get('tags', [])][:4]
            
            score_up = post_data.get('score', 0) 
            score_down = 0  
            
            content = (
                f"🌍 Post ID: {post_id}\n"
                f"🌟 Tags: {', '.join(tags)}\n"
                f"📸 Posted by {username}\n"
                f"👍 Votings: up: {score_up} down: {score_down}\n"
                f"🌐 Post URL: {post_url}"
            )
            
            # Create thumbnail URL
            thumbnail_url = f"{SZURU_API_URL}/data/thumbnails/{post_data['thumbnailUrl']}"
            
            print("Waiting 5 seconds before posting...")
            time.sleep(5)
            
            post_uri = post_to_bluesky(jwt, did, content, thumbnail_url)
            
            if post_uri:
                print(f"Post ID {post_id} posted to Bluesky")
            
            post_id += 1  # Move to the next post ID

            # Wait 2 hours before the next post
            print("Waiting 2 hours before the next post...")
            time.sleep(2 * 60 * 60)  # 2 hours * 60 minutes * 60 seconds
        
        else:
            # If no valid post is found, move to the next post ID
            print(f"No valid post found for ID {post_id}. Moving to the next ID.")
            post_id += 1
            time.sleep(1)

if __name__ == "__main__":
    post_loop()
