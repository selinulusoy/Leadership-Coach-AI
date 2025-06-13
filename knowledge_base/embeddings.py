from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def get_embedding_model():
    model = SentenceTransformer(EMBEDDING_MODEL)
    return model

def generate_embeddings(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """
    Generate embeddings for text chunks
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings.tolist()