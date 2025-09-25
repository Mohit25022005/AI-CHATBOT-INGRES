from dotenv import load_dotenv
from pydantic import BaseSettings

# Load environment variables from .env
load_dotenv()

class Settings(BaseSettings):
    # Local ML model settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # SentenceTransformer
    LLM_MODEL: str = "tiiuae/falcon-7b-instruct"  # Hugging Face model, 4-bit quantization

    # Optional external services
    JIRA_API_TOKEN: str = ""
    JIRA_BASE_URL: str = ""
    JIRA_PROJECT_KEY: str = ""
    FRONTEND_ORIGIN: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
