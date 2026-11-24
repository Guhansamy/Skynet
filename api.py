from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from shared.llm import get_model
from shared.prompts import load_prompt

app = FastAPI(title="Skynet")

agent = Agent(
    get_model(),
    system_prompt=load_prompt("orchestrator"),
)

@agent.tool_plain
def get_time() -> str:
    """Return the current date and time."""
    return datetime.now().isoformat()

class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    result = await agent.run(body.message)
    return ChatOut(reply=result.output)
