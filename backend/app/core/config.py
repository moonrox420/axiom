from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Axiom"
    app_version: str = "0.1.0"
    debug: bool = False
    
    database_url: str = "postgresql+psycopg://axiom:axiom@localhost:5432/axiom_db"
    redis_url: str = "redis://localhost:6379/0"
    
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    s3_bucket_name: str = "axiom-documents"
    s3_region: str = "us-east-1"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    
    sentry_dsn: str = ""
    
    default_currency: str = "USD"
    default_tax_rate: float = 0.0825
    default_payment_terms_days: int = 14
    
    max_upload_size_mb: int = 50
    max_exception_queue_size: int = 500
    
    smtp_host: str = "smtp.sendgrid.net"
    smtp_port: int = 587
    smtp_user: str = "apikey"
    smtp_password: str = ""
    smtp_from_email: str = "noreply@axiom.local"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()