import json
from typing import List


def chunk_transcript(file_path: str) -> List[dict]:
    """
    Process transcript JSON into chunks with timing 
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        video_id = data.get("video_id", "")
        chunks = []
        
        for event in data.get("segments", {}).get("events", []):
            if not isinstance(event, dict):
                continue
                
            if "segs" not in event or "tStartMs" not in event:
                continue
                
            text_parts = []
            for seg in event["segs"]:
                if isinstance(seg, dict) and seg.get("utf8", "").strip() not in ("", "\n"):
                    text_parts.append(seg["utf8"].strip())
            
            if not text_parts:
                continue
                
            full_text = " ".join(text_parts)
            start_time = event["tStartMs"] / 1000  # convert ms to seconds
            
            chunks.append({
                "video_id": video_id,
                "text": full_text,
                "start_time": start_time
            })

        return chunks

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []
    
# def basic_chunk_transcript(file_path: str) -> List[str]:
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         video_id = data.get("video_id", "")
#         chunks = []
#         for event in data.get("segments", {}).get("events", []):
#             if "segs" in event:
#                 chunk = ''.join(seg.get('utf8', '') for seg in event['segs'])
#                 chunks.append(chunk)

#         return chunks

#     except FileNotFoundError:
#         print(f"File not found: {file_path}")
#         return []
#     except json.JSONDecodeError:
#         print(f"Error decoding JSON from file: {file_path}")
#         return []
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return []

