# app/utils/config.py
from dotenv import load_dotenv
from pydantic import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    JIRA_API_TOKEN: str = ""
    JIRA_BASE_URL: str = ""
    JIRA_PROJECT_KEY: str = ""
    FRONTEND_ORIGIN: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
