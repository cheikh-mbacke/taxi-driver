from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base de données
    database_url: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "taxi_driver"
    postgres_user: str = "taxi_user"
    postgres_password: str = "taxi_password"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # ML
    model_save_path: str = "./data/models"
    results_save_path: str = "./data/results"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
