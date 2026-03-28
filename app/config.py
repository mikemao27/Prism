from pydantic_settings import BaseSettings, SettingsConfigDict

# Create a new Settings class that inherits from BaseSettings.
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GEMINI_API_KEY: str
    DATABASE_URL: str
    REDIS_URL: str

    model_config = SettingsConfigDict(env_file=".env")

# Instantiate a new instance of settings = Settings().
settings = Settings()