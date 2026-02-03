from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Entropy"
    LM_STUDIO_BASE_URL: str = "http://127.0.0.1:1234/v1/"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
