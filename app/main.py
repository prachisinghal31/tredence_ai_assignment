# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .graph_engine import engine
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    GraphStateResponse,
)
from .tools import DEFAULT_CODE_REVIEW_GRAPH_ID  # ensures tools + default graph are registered


app = FastAPI(title="Tredence Mini LangGraph Engine", version="0.1.0")

# Enable CORS if you later plug a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Mini workflow engine is running.",
        "default_code_review_graph_id": DEFAULT_CODE_REVIEW_GRAPH_ID,
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(payload: GraphCreateRequest):
    graph = engine.create_graph(
        nodes=payload.nodes, edges=payload.edges, entrypoint=payload.entrypoint
    )
    return GraphCreateResponse(graph_id=graph.id)


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(req: GraphRunRequest):
    try:
        _ = engine.get_graph(req.graph_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")

    run = await engine.run_graph(req.graph_id, req.initial_state)
    return GraphRunResponse(run_id=run.id, final_state=run.state, log=run.log)


@app.get("/graph/state/{run_id}", response_model=GraphStateResponse)
async def get_graph_state(run_id: str):
    try:
        run = engine.get_run(run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Run not found")

    return GraphStateResponse(
        run_id=run.id,
        graph_id=run.graph_id,
        state=run.state,
        status=run.status.value,
        current_node=run.current_node,
    )
