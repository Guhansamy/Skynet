from datetime import date
from typing import TypedDict, Optional
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from ddgs import DDGS

qwen = ChatOllama(model="qwen3.5:9b", temperature=0)
gemma = ChatOllama(model="gemma3:4b", temperature=0)

class Request(BaseModel):
    movie: Optional[str] = None
    city: Optional[str] = None
    seats: Optional[int] = None
    date: Optional[str] = None

class State(TypedDict):
    question: str
    request: dict
    results: list[dict]
    answer: str

def planner(state: State) -> dict:
    extractor = qwen.with_structured_output(Request)
    req = extractor.invoke(
        "Extract movie, city, seats and date from this request. "
        f"Use null for anything not mentioned.\n\n{state['question']}"
    )
    return {"request": req.model_dump()}

def search(state: State) -> dict:
    r = state["request"]
    if not r["movie"] or not r["city"]:
        return {"results": []}
    query = " ".join(p for p in [r["movie"], "movie tickets", r["city"], r["date"]] if p)
    hits = DDGS().text(query, max_results=8)
    movie = r["movie"].lower()
    results = [
        {"title": h["title"], "url": h["href"], "snippet": h["body"]}
        for h in hits
        if movie in (h["title"] + h["body"] + h["href"]).lower()
    ]
    return {"results": results}

def writer(state: State) -> dict:
    r = state["request"]
    if not r["movie"]:
        return {"answer": "Which movie do you want tickets for?"}
    if not r["city"]:
        return {"answer": f"Which city should I check for {r['movie']}?"}
    if not state["results"]:
        return {"answer": "not found"}
    msg = (
        f"Today is {date.today():%A, %d %B %Y}.\n"
        f"User wants {r['seats'] or 'any number of'} seats for {r['movie']} "
        f"in {r['city']} ({r['date'] or 'any date'}).\n"
        "Rules:\n"
        "1. Use ONLY the search results below.\n"
        "2. Skip results whose date is far from today.\n"
        "3. Format each item as a bullet: - Site: link (short reason). No dicts, no JSON.\n"
        "4. Never claim seats are available. Say seat availability must be checked on the site.\n"
        "5. If nothing relevant remains, reply exactly: not found.\n\n"
        f"{state['results']}"
    )
    return {"answer": gemma.invoke(msg).content.strip()}

graph = StateGraph(State)
graph.add_node("planner", planner)
graph.add_node("search", search)
graph.add_node("writer", writer)
graph.add_edge(START, "planner")
graph.add_edge("planner", "search")
graph.add_edge("search", "writer")
graph.add_edge("writer", END)

movie_graph = graph.compile()