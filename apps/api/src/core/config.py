from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://mindvpn:mindvpn_dev@localhost:5432/mindvpn"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "dev_secret_key_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # mTLS Certificates
    ca_cert_path: str = "certs/ca.crt"
    server_cert_path: str = "certs/server.crt"
    server_key_path: str = "certs/server.key"
    
    # API
    api_v1_prefix: str = "/v1"
    project_name: str = "MindVPN"
    version: str = "1.0.0"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://ui:3000"]
    
    # Monitoring
    prometheus_port: int = 9090
    
    # Agent settings
    agent_heartbeat_interval: int = 15  # seconds
    agent_timeout: int = 30  # seconds
    
    # Task settings
    task_timeout: int = 300  # seconds
    task_retry_attempts: int = 3
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Override with environment variables if present
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")
if os.getenv("REDIS_URL"):
    settings.redis_url = os.getenv("REDIS_URL")
if os.getenv("SECRET_KEY"):
    settings.secret_key = os.getenv("SECRET_KEY")
if os.getenv("CA_CERT_PATH"):
    settings.ca_cert_path = os.getenv("CA_CERT_PATH")
if os.getenv("SERVER_CERT_PATH"):
    settings.server_cert_path = os.getenv("SERVER_CERT_PATH")
if os.getenv("SERVER_KEY_PATH"):
    settings.server_key_path = os.getenv("SERVER_KEY_PATH")
