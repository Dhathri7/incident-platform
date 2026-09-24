import os
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    database_test_url: str
    
    # JWT Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    
    # FAISS
    faiss_index_path: str = "./rag/vector_store/incidents.index"
    embeddings_model: str = "all-MiniLM-L6-v2"
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()