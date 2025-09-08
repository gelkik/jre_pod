import boto3
import gzip
import json
import os
from dotenv import load_dotenv
load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET = os.getenv("S3_BUCKET")
def read_from_s3(title):
    key = f"transcripts/{title}.json.gz"

    response = s3.get_object(Bucket=BUCKET, Key=key)
    compressed_data = response['Body'].read()
    data = json.loads(gzip.decompress(compressed_data).decode("utf-8"))

    print(data)

if __name__ == "__main__":
    with open("videos.json", "r", encoding="utf-8") as f:
        videos = json.load(f)
        for video in videos[0:1]:
            read_from_s3(video["title"])