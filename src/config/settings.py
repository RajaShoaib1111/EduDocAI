"""Configuration settings for EduDocAI application.

This module defines all application settings using Pydantic for validation.
Settings are loaded from environment variables using python-dotenv.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be configured via .env file or environment variables.
    See .env.example for available options.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for LLM and embeddings"
    )

    # LangChain/LangSmith Configuration
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangSmith tracing for debugging"
    )
    langchain_api_key: str | None = Field(
        default=None,
        description="LangSmith API key (optional, for tracing)"
    )

    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./data/vector_db",
        description="Directory for ChromaDB persistence"
    )

    # Document Processing Settings
    chunk_size: int = Field(
        default=1000,
        description="Size of text chunks for document splitting",
        ge=100,
        le=4000
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between chunks",
        ge=0,
        le=1000
    )

    # Retrieval Settings
    top_k_results: int = Field(
        default=4,
        description="Number of document chunks to retrieve",
        ge=1,
        le=20
    )

    # File Upload Settings
    max_file_size_mb: int = Field(
        default=10,
        description="Maximum file upload size in MB",
        ge=1,
        le=100
    )

    # Model Configuration
    llm_model: str = Field(
        default="gpt-4o",
        description="OpenAI model for LLM generation"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI model for embeddings"
    )
    temperature: float = Field(
        default=0.0,
        description="LLM temperature for generation",
        ge=0.0,
        le=2.0
    )

    # Application Settings
    app_name: str = Field(
        default="EduDocAI",
        description="Application name"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings: The application settings
    """
    return settings
