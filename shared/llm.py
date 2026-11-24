from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

OLLAMA_URL = "http://localhost:11434/v1"

def get_model(name: str = "qwen3.5:9b") -> OpenAIChatModel:
    return OpenAIChatModel(
        name,
        provider=OpenAIProvider(base_url=OLLAMA_URL, api_key="ollama"),
    )
