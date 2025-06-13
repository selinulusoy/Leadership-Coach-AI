import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    register_vector(conn)
    return conn

def create_knowledge_table(conn):
    """
    Create table for storing knowledge base
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                video_id VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                start_time FLOAT NOT NULL,
                embedding VECTOR(384)  -- Dimension for multilingual MiniLM
            );
            CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
        """)
        conn.commit()

def insert_chunks(conn, chunks: list[dict]):
    """
    Insert chunks with embeddings 
    """
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE knowledge_base")
        
        insert_sql = """
            INSERT INTO knowledge_base 
                (video_id, content, start_time, embedding) 
            VALUES 
                (%s, %s, %s, %s)
        """
        # batch data
        batch_data = [
            (
                chunk["video_id"],
                chunk["content"],
                chunk["start_time"],
                chunk["embedding"]
            )
            for chunk in chunks
        ]
        
        # batch insert
        cursor.executemany(insert_sql, batch_data)
        conn.commit()
        
        print(f"✅ Inserted {len(chunks)} chunks")
        
