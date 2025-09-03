from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
CHANNEL_ID = "UCzQUP1qoWDoEbmsQxvdjxgQ"
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_videos():
    channel_rep = youtube.channels().list(
        part="contentDetails",
        id=CHANNEL_ID
    ).execute()
    uploads_playlist_id = channel_rep["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    # print(uploads_playlist_id)

    videos = []
    next_page_token = None

    while True:
        playlist_items = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        videos.extend(playlist_items["items"])
        next_page_token = playlist_items.get("nextPageToken")

        if not next_page_token:
            break

    # for video in videos[0:5]:
    #     video_id = video["snippet"]["resourceId"]["videoId"]
    #     print(video_id)

    return videos

# all_ids = get_videos()

