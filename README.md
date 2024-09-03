# Bluesky Post Automation Script

This script automates the process of posting content from f0ck.org to Bluesky. It periodically fetches posts from f0ck.org, formats them, and posts them to Bluesky with the relevant information.

## Features

- **Automated Posting**: Automatically posts content from f0ck.org to Bluesky.
- **Content Formatting**: Formats the post with URLs, comments, tags, and user information.
- **Scheduled Posting**: Posts every 6 hours or skips to the next post if no valid content is found.

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/ninjazan420/bluesky-post-automation.git
    cd bluesky-post-automation
    ```

2. **Install dependencies**:

    ```bash
    pip install requests
    ```

3. **Update Configuration**:

    Open the script file `bluesky_bot.py` and replace the placeholders for `USERNAME` and `PASSWORD` with your Bluesky credentials.

## Usage

1. **Run the script**:

    ```bash
    python bluesky_bot.py
    ```

2. **How it works**:
   - The script logs into Bluesky using your credentials.
   - It starts fetching posts from f0ck.org starting from ID 1.
   - For each valid post, it formats the content and posts it to Bluesky.
   - If a post is not found, it skips to the next ID and retries.

## Post Format

Each post on Bluesky will be formatted as follows:

![grafik](https://github.com/user-attachments/assets/6b973650-5a19-4aba-b79c-1c8c648653fa)



