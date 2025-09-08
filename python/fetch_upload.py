import os, json, gzip
from youtube_transcript_api import YouTubeTranscriptApi
from ytpull import get_videos
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Code connects to S3, checks if video transcripts already exist, and then processes new videos
load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

FILENAME = "videos.json" 
BUCKET = os.getenv("S3_BUCKET")

def s3_key_exists(bucket: str, key: str) -> bool:
    """Return True if `key` exists in `bucket`, False if not."""
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        code = e.response["Error"]["Code"]
        # 404 or NoSuchKey means “not found”
        if code in ("404", "NoSuchKey"):
            return False
        raise

def fetch_transcript(video_id,title,publishedAt):

    # Checks json file to see if video has already been processed
    with open(FILENAME, "r", encoding="utf-8") as f:
        videos = json.load(f)

    key = f'transcripts/{title}.json.gz'

    if s3_key_exists(BUCKET, key):
        print(f"Skipping {title}, already processed.")
        videos["video_id"==video_id]["processed"] = True
        return
    # If video is not in json file, it adds it
    elif video_id not in [video["video_id"] for video in videos]:
        videos.append({
            "video_id": video_id,
            "title": title,
            "publishedAt": publishedAt,
            "processed": True
        })

    # Writes to JSON dictionary whether it has been processed or not
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    # If not processed, then API will commence
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id=video_id)
        transcript_list = [
            {"text": snippet.text, "start": snippet.start, "duration": snippet.duration}
            for snippet in transcript
        ]
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return "ERROR"

    data = {"title": title,"video_id": video_id, "transcript": transcript_list}

    compressed = gzip.compress(json.dumps(data).encode("utf-8"))

    key = f"transcripts/{title}.json.gz"
    try:
        s3.put_object(Bucket=BUCKET, Key=key, Body=compressed)
        print(f"Uploaded {title} to s3://{BUCKET}/{key}")
    except Exception as e:
        print(f"Error uploading {title} to S3: {e}")



if __name__ == "__main__":
    all_videos = get_videos()
    for video in all_videos:
        result = fetch_transcript(video["snippet"]["resourceId"]["videoId"], video["snippet"]["title"],video["snippet"]["publishedAt"])
        if result == "ERROR":
            break