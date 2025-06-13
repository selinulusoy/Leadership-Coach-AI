import os
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(EMBEDDING_MODEL)

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

def retrieve_from_knowledge_base(query: str, threshold: float = 0.65) -> tuple:
    """
    Retrieve relevant content from YouTube knowledge base
    """
    query_embedding = model.encode([query])[0]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # vector search with pgvector
    cursor.execute("""
        SELECT 
            content, 
            video_id, 
            start_time,
            1 - (embedding <=> %s) as similarity
        FROM knowledge_base
        WHERE embedding <=> %s < %s
        ORDER BY similarity DESC
        LIMIT 5
    """, (query_embedding, query_embedding, 1 - threshold))
    
    results = cursor.fetchall()
    max_similarity = max([r[3] for r in results]) if results else 0.0
    return results, max_similarity