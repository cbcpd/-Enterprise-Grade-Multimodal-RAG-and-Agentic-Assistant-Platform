from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_dir: str = "./chroma_db"
    collection_name: str = "enterprise_documents"
    upload_dir: str = "./uploads"
    feedback_file: str = "./data/feedback.jsonl"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    max_file_mb: int = 25

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
