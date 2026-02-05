from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Directories
    DATA_DIR: str = "./data"
    UPLOAD_DIR: str = "./data/uploads"
    INDEX_DIR: str = "./data/faiss_index"
    TEMP_DIR: str = "./data/temp"

    # Chunking
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 80

    # Upload
    MAX_FILE_SIZE_MB: int = 50

    # Models
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Embedding dimension for the multilingual model
    EMBEDDING_DIMENSION: int = 384

    class Config:
        env_file = ".env"
        case_sensitive = True

    def ensure_directories(self):
        """Create data directories if they don't exist"""
        for dir_path in [self.DATA_DIR, self.UPLOAD_DIR, self.INDEX_DIR, self.TEMP_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
