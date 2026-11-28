from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from shared.llm import get_model
from shared.prompts import load_prompt
from agents.movie_graph import movie_graph

app = FastAPI(title="Skynet")

agent = Agent(
    get_model(),
    system_prompt=load_prompt("orchestrator"),
)

# tools for the agent
@agent.tool_plain
def get_time() -> str:
    """Return the current date and time."""
    return datetime.now().isoformat()

@agent.tool_plain
def find_movie_tickets(request: str) -> str:
    """Find where to book movie tickets. Use for any request about movie
    tickets, seats, showtimes or booking. Pass the user's full request,
    for example '5 seats for Scene in Coimbatore this Saturday'."""
    return movie_graph.invoke({"question": request})["answer"]

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
