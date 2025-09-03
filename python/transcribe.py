from youtube_transcript_api import YouTubeTranscriptApi
from ytpull import get_videos

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id=video_id)
        return transcript
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
all_videos = get_videos()
# print(fetch_transcript(all_videos[0]["snippet"]["resourceId"]["videoId"]))
