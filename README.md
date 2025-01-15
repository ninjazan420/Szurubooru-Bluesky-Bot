# Bluesky Post Automation Script

This script automates the process of posting content from a running [Szurubooru-instance](https://github.com/rr-/szurubooru) to Bluesky. It periodically fetches posts via API, formats them, and posts them to Bluesky with the relevant information.

## Features

- **Automated Posting**: Automatically posts content from Szurubooru to [Bluesky](https://bsky.app/profile/f0ck.org).
- **Content Formatting**: Formats the post with URLs, comments, tags, and user information.
- **Scheduled Posting**: Posts every 6 hours or skips to the next post if no valid content is found.

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/ninjazan420/Szurubooru-Bluesky-Bot.git
    cd Szurubooru-Bluesky-Bot
    ```

2. **Install dependencies**:

    ```bash
    pip install requirements.txt
    ```

3. **Update Configuration**:

    Open the script file `bluesky_bot.py` and replace the placeholders for `USERNAME` and `PASSWORD` with your Bluesky credentials.
    Also change the URLHERE to your actual URL, but do not change /api!

## Usage

1. **Run the script**:

    ```bash
    python bluesky_bot.py
    ```

2. **How it works**:
   - The script logs into Bluesky using your credentials.
   - It starts fetching posts from your instance starting from ID 1.
   - For each valid post, it formats the content and posts it to Bluesky.
   - If a post is not found, it skips to the next ID and retries.


![grafik](https://github.com/user-attachments/assets/d066490c-1e7d-4ea7-a08c-4f31d68021c8)



## Post Format

Each post on Bluesky will be formatted as follows:

![grafik](https://github.com/user-attachments/assets/468fc6da-4172-42d8-8c79-d189dc300194)



