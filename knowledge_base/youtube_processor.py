import os
import re
import json
import time
import random
from pytubefix import Playlist, YouTube

# configuration
MAX_RETRIES = 10
RETRY_DELAY = 5
RETRY_DELAY_TRANSCRIPT = 6

def get_playlist_metadata(playlist_url: str) -> list[dict]:
    """
        Extract video metadata using pytubefix 
    """
    try:
        playlist = Playlist(playlist_url)
        playlist._video_regex = re.compile(r'{"url":"/watch\?v=([^"]+)"')
        
        videos = []        
        for i, video_url in enumerate(playlist.video_urls):
            print(f"\nProcessing video {i+1}: {video_url}")
            for attempt in range(MAX_RETRIES):
                try:
                    yt = YouTube(
                        video_url,
                        use_oauth=True,
                        allow_oauth_cache=True
                    )
                    videos.append({
                        "id": yt.video_id,
                        "title": yt.title,
                        "url": video_url,
                        "duration": yt.length
                    })
                    print(f"Added: {yt.title[:50]}")
                    break
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        # wait before retry
                        time.sleep(RETRY_DELAY)
                    else:
                        print(f"Failure processing video: {video_url}")
                        break
        return videos
        
    except Exception as e:
        print(f"Playlist error: {str(e)}")
        return []


def get_caption(video_url: str) -> list[dict]:
    """
        Access to video transcripts usin pytubefix.
    """
    for i in range(MAX_RETRIES):
        try:
            yt = YouTube(
                    video_url,
                    use_oauth=True,
                    allow_oauth_cache=True
                    )
            caption = yt.captions['a.en']
            #caption.save_captions("captions.txt")
            with open('video_captions.json', 'w') as f:
                json.dump(caption.json_captions, f)

            return caption.json_captions
        except Exception as e:
            print(f"Error: {type(e).__name__}: {str(e)}")
            time.sleep(RETRY_DELAY_TRANSCRIPT)
            return []

def save_transcript(video_id: str, segments: list[dict], output_dir: str = "transcripts"):
    """Save structured transcript data to JSON"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        with open(f"{output_dir}/{video_id}.json", "w", encoding="utf-8") as f:
            json.dump({
                "video_id": video_id,
                "segments": segments
            }, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"Failed to save transcript: {str(e)}")
        return False
    

def process_playlist(playlist_url: str, force_refresh: bool = False):
    """
    Playlist scraping pipeline 
    """
    print(f"Processing playlist")
    metadata_file = "playlist_metadata.json"
    
    # load existing metadata if available
    if not force_refresh and os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            videos = json.load(f)
        print(f"Loaded metadata for {len(videos)} videos from cache")
    else:
        # get metadata if no cache exists
        videos = get_playlist_metadata(playlist_url)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        print(f"\nSaved metadata for {len(videos)} videos")
    
    successful_videos = []
    os.makedirs("transcripts", exist_ok=True)
    for i, video in enumerate(videos):
        transcript_path = f"transcripts/{video['id']}.json"
        
        if not force_refresh and os.path.exists(transcript_path):
            print(f"Skipping processed video {i+1}/{len(videos)}: {video['title'][:50]}...")
            successful_videos.append(video['id'])
            continue
            
        print(f"\nProcessing video {i+1}/{len(videos)}: {video['title'][:50]}...")
        print(f"Video ID: {video['id']}")
        
        if i > 0:
            delay = random.uniform(2, 5)
            print(f"Waiting {delay:.1f}s before next request...")
            time.sleep(delay)
        
        segments = get_caption(video["url"])
        
        if segments:
            print(f"Found {len(segments)} caption segments")
            if save_transcript(video["id"], segments):
                successful_videos.append(video["id"])
                print(f"✅ Saved transcript for {video['id']}")
            else:
                print(f"❌ Failed to save transcript for {video['id']}")
        else:
            print(f"⚠️ Skipped {video['id']}: No segments found")
    
    print(f"\nProcessing complete! {len(successful_videos)}/{len(videos)} videos processed")
    return successful_videos

# test execution
if __name__ == "__main__":

    playlist_url = "https://www.youtube.com/playlist?list=PLCi3Q_-uGtdlCsFXHLDDHBSLyq4BkQ6gZ"
    process_playlist(playlist_url)
