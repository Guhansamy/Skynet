# from datetime import datetime
# from fastapi import FastAPI
# from pydantic import BaseModel
# from pydantic_ai import Agent
# from shared.llm import get_model
# from shared.prompts import load_prompt
# from agents.movie_graph import movie_graph

# app = FastAPI(title="Skynet")

# agent = Agent(
#     get_model(),
#     system_prompt=load_prompt("orchestrator"),
# )

# chat_agent = Agent(
#     get_model("gemma3:4b"),
#     system_prompt=load_prompt("chat"),
# )

# TASK_WORDS = ("ticket", "seat", "movie", "show", "book", "price", "time", "track", "alert")

# def is_task(message: str) -> bool:
#     m = message.lower()
#     return any(w in m for w in TASK_WORDS)

# @app.post("/chat", response_model=ChatOut)
# async def chat(body: ChatIn):
#     if is_task(body.message):
#         result = await agent.run(body.message)      # Qwen + tools
#     else:
#         result = await chat_agent.run(body.message) # fast model
#     return ChatOut(reply=result.output)

# @agent.tool_plain
# def get_time() -> str:
#     """Return the current date and time."""
#     return datetime.now().isoformat()

# @agent.tool_plain
# def find_movie_tickets(request: str) -> str:
#     """Find where to book movie tickets. Use for any request about movie
#     tickets, seats, showtimes or booking. Pass the user's full request,
#     for example '5 seats for Scene in Coimbatore this Saturday'."""
#     return movie_graph.invoke({"question": request})["answer"]

# class ChatIn(BaseModel):
#     message: str

# class ChatOut(BaseModel):
#     reply: str

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/chat", response_model=ChatOut)
# async def chat(body: ChatIn):
#     result = await agent.run(body.message)
#     return ChatOut(reply=result.output)



from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from shared.llm import get_model
from shared.prompts import load_prompt
from agents.movie_graph import movie_graph

app = FastAPI(title="Skynet")

# ---------- models for request and reply ----------
class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str

# ---------- agents ----------
agent = Agent(get_model(), system_prompt=load_prompt("orchestrator"))
chat_agent = Agent(get_model("gemma3:4b"), system_prompt=load_prompt("chat"))

# ---------- tools (Qwen only) ----------
@agent.tool_plain
def get_time() -> str:
    """Return the current date and time."""
    return datetime.now().isoformat()

@agent.tool_plain
async def find_movie_tickets(request: str) -> str:
    """Find where to book movie tickets. Use for any request about movie
    tickets, seats, showtimes or booking. Pass the user's full request,
    for example '5 seats for Scene in Coimbatore this Saturday'."""
    out = await movie_graph.ainvoke({"question": request})
    return out["answer"]

# ---------- router ----------
TASK_WORDS = ("ticket", "seat", "movie", "show", "book", "price", "time", "track", "alert")

def is_task(message: str) -> bool:
    m = message.lower()
    return any(w in m for w in TASK_WORDS)

# ---------- endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    if is_task(body.message):
        result = await agent.run(body.message)       # Qwen + tools
    else:
        result = await chat_agent.run(body.message)  # fast model
    return ChatOut(reply=result.output)