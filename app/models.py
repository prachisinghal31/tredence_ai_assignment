# app/models.py
from typing import Dict, Any, List
from pydantic import BaseModel
from .graph_engine import NodeConfig, EdgeConfig


class GraphCreateRequest(BaseModel):
    nodes: Dict[str, NodeConfig]
    edges: Dict[str, EdgeConfig]
    entrypoint: str


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = {}


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[Dict[str, Any]]


class GraphStateResponse(BaseModel):
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    status: str
    current_node: Any
