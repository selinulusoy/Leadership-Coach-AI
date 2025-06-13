import os
from dotenv import load_dotenv
from knowledge_base.youtube_processor import process_playlist
from knowledge_base.chunk_processor import chunk_transcript
from knowledge_base.embeddings import generate_embeddings
from knowledge_base.db_operations import get_db_connection, create_knowledge_table, insert_chunks
load_dotenv()  

def main():
    """
    Pipeline for knowledge base creation
    """

    print("Scrape YouTube playlist")
    playlist_url = "https://www.youtube.com/playlist?list=PLCi3Q_-uGtdlCsFXHLDDHBSLyq4BkQ6gZ"
    processed_videos = process_playlist(playlist_url)
    print(f"Transcript files found: {len(os.listdir('transcripts'))}")
   
    print("Process all transcripts into chunks")
    all_chunks = []
    for video_id in processed_videos:
        transcript_path = f"transcripts/{video_id}.json"
        try:
            chunks = chunk_transcript(transcript_path)
            all_chunks.extend(chunks)
            print(f"Chunks generated: {len(chunks)}")
        except Exception as e:
            print(f"Error processsing chunks for video {video_id}: {e}")

    print("Generate embeddings for text")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = generate_embeddings(texts)
    
    print("Prepare chunks for DB insertion") 
    knowledge_chunks = [
        {
            "video_id": chunk["video_id"],
            "content": chunk["text"],
            "start_time": chunk["start_time"],
            "embedding": embeddings[i]
        }
        for i, chunk in enumerate(all_chunks)
    ]

    print("Insert into PostgreSQL/pgvector")
    conn = get_db_connection()
    create_knowledge_table(conn)
    insert_chunks(conn, knowledge_chunks)
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    conn.close()
    print(f"Knowledge base is ready!")

if __name__ == "__main__":
    main()