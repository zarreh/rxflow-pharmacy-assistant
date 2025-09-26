"""
Configuration Management for RxFlow Pharmacy Assistant
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings configuration"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="RxFlow Pharmacy Assistant", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2", alias="OLLAMA_MODEL")
    
    # Alternative LLM configurations (for future use)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    
    # Mock Data
    use_mock_data: bool = Field(default=True, alias="USE_MOCK_DATA")
    
    # Vector Store
    embeddings_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        alias="EMBEDDINGS_MODEL"
    )
    vector_store_path: str = Field(default="./data/vector_store", alias="VECTOR_STORE_PATH")
    
    # Demo Configuration
    demo_patient_id: str = Field(default="patient_001", alias="DEMO_PATIENT_ID")
    demo_insurance_id: str = Field(default="BCBS_TX_001", alias="DEMO_INSURANCE_ID")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings