"""
PromptGuard Configuration Settings
Enterprise-grade configuration with environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # ==========================================
    # Server Configuration
    # ==========================================
    APP_NAME: str = "PromptGuard API v2.0"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = os.getenv("FLASK_ENV", "development")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 5000))
    WORKERS: int = int(os.getenv("WORKERS", 4))
    RELOAD: bool = ENVIRONMENT == "development"
    
    # ==========================================
    # CORS Configuration
    # ==========================================
    ALLOWED_ORIGINS: list = (
        os.getenv("ALLOWED_ORIGINS", "*").split(",")
        if os.getenv("ALLOWED_ORIGINS")
        else ["*"]
    )
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]
    
    # ==========================================
    # API Configuration
    # ==========================================
    MAX_PROMPT_LENGTH: int = 2000
    MIN_PROMPT_LENGTH: int = 1
    API_TIMEOUT: int = 30  # seconds
    
    # ==========================================
    # Cache Configuration
    # ==========================================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour
    ENABLE_REDIS: bool = os.getenv("ENABLE_REDIS", "true").lower() == "true"
    
    # ==========================================
    # Database Configuration
    # ==========================================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )
    DB_ECHO: bool = DEBUG
    DB_POOL_SIZE: int = 20
    DB_POOL_RECYCLE: int = 3600
    
    # ==========================================
    # LLM Configuration
    # ==========================================
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 16384
    LLM_TIMEOUT: int = 30
    
    # ==========================================
    # ML Model Configuration
    # ==========================================
    ML_MODEL_NAME: str = "ProtectAI/deberta-v3-base-prompt-injection-v2"
    ML_DEVICE: str = "auto"  # auto, cpu, cuda
    ML_BATCH_SIZE: int = 8
    ML_MAX_LENGTH: int = 512
    ML_TRUNCATION: bool = True
    
    # Semantic models
    SEMANTIC_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"
    SEMANTIC_EMBEDDING_DIM: int = 384
    
    # ==========================================
    # Security Configuration
    # ==========================================
    # Risk thresholds
    ML_SCORE_THRESHOLD: float = 0.98
    RISK_SCORE_THRESHOLD: float = 0.55
    SOFT_CHALLENGE_THRESHOLD: float = 0.50
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.75
    
    # Adaptive learning
    ADAPTIVE_LEARNING_ENABLED: bool = True
    ADAPTIVE_PROMOTION_THRESHOLD: int = 3
    ADAPTIVE_LEARNING_MIN_CONFIDENCE: float = 0.7
    
    # ==========================================
    # Monitoring Configuration
    # ==========================================
    METRICS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8000
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "false").lower() == "true"
    JAEGER_HOST: str = os.getenv("JAEGER_HOST", "localhost")
    JAEGER_PORT: int = int(os.getenv("JAEGER_PORT", 6831))
    
    # ==========================================
    # Logging Configuration
    # ==========================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, text
    ENABLE_STRUCTURED_LOGGING: bool = True
    
    # ==========================================
    # Feature Flags
    # ==========================================
    ENABLE_INTENT_CLASSIFICATION: bool = True
    ENABLE_CONTEXT_TRACKING: bool = True
    ENABLE_ESCALATION_DETECTION: bool = True
    ENABLE_SEMANTIC_ANALYSIS: bool = True
    ENABLE_POLICY_ENGINE: bool = True
    ENABLE_SHADOW_EVALUATION: bool = os.getenv("ENABLE_SHADOW", "false").lower() == "true"
    ENABLE_ASYNC_LLM: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
