"""Application configuration for the Document Q&A API."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Document Q&A API"
    app_version: str = "1.0.0"
    debug: bool = False

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    max_tokens: int = 1500

    # Document limits
    max_document_length: int = 50000  # Max chars per document
    max_documents: int = 100  # Max documents stored at once
    max_question_length: int = 1000  # Max chars per question

    # Context window management
    # When a document is too long to send entirely to the AI,
    # we truncate it to this many characters.
    # gpt-4o-mini supports 128k tokens, but shorter contexts
    # give better answers and cost less.
    context_max_chars: int = 15000

    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()


"""
Configuration - loaded from environment variables.
Phase 1 pattern reused unchanged, with 2 new settings added.
"""
from pydantic_settings import BaseSettings
 
class Settings(BaseSettings):
    # Phase 1 settings (unchanged)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    max_tokens: int = 1000
    log_level: str = "INFO"
 
    # Phase 2 NEW settings
    embedding_model: str = "text-embedding-3-small"
    chroma_path: str = "./chroma_db"
 
    class Config:
        env_file = ".env"
 
settings = Settings()

