from pydantic import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    streamlit_port: int = 8501

    class Config:
        env_file = ".env"


settings = Settings()
