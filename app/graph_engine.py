# app/graph_engine.py
from typing import Dict, Any, Callable, Optional, List
from enum import Enum
from pydantic import BaseModel
import uuid


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class NodeConfig(BaseModel):
    """
    Configuration for a node in the graph.
    Each node simply points to a tool name in the registry.
    """
    tool: str


class EdgeConfig(BaseModel):
    """
    Edge configuration for routing from one node to the next.
    - next: default next node
    - condition_key / gte / lt / if_true / if_false: basic conditional routing
    """
    next: Optional[str] = None
    condition_key: Optional[str] = None  # key in the state dict to look at
    gte: Optional[float] = None
    lt: Optional[float] = None
    if_true: Optional[str] = None
    if_false: Optional[str] = None


class Graph(BaseModel):
    id: str
    nodes: Dict[str, NodeConfig]
    edges: Dict[str, EdgeConfig]
    entrypoint: str


class Run(BaseModel):
    id: str
    graph_id: str
    state: Dict[str, Any]
    log: List[Dict[str, Any]]
    status: RunStatus
    current_node: Optional[str] = None


class ToolRegistry:
    """
    Very simple in-memory registry of Python functions (tools).
    Tool signature: (state: Dict[str, Any]) -> Dict[str, Any]
    They read+modify the shared state.
    """

    def __init__(self):
        self._tools: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self._tools[name] = func

    def get(self, name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())


tool_registry = ToolRegistry()


class GraphEngine:
    """
    Minimal workflow / graph engine:
    - Keeps graphs in memory
    - Keeps runs in memory
    - Executes nodes in sequence with simple conditionals + loop support
    """

    def __init__(self):
        self.graphs: Dict[str, Graph] = {}
        self.runs: Dict[str, Run] = {}

    def create_graph(
        self,
        nodes: Dict[str, NodeConfig],
        edges: Dict[str, EdgeConfig],
        entrypoint: str,
    ) -> Graph:
        graph_id = str(uuid.uuid4())
        graph = Graph(id=graph_id, nodes=nodes, edges=edges, entrypoint=entrypoint)
        self.graphs[graph_id] = graph
        return graph

    def get_graph(self, graph_id: str) -> Graph:
        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found")
        return self.graphs[graph_id]

    def get_run(self, run_id: str) -> Run:
        if run_id not in self.runs:
            raise KeyError(f"Run '{run_id}' not found")
        return self.runs[run_id]

    async def run_graph(
        self,
        graph_id: str,
        initial_state: Dict[str, Any],
        max_steps: int = 50,
    ) -> Run:
        """
        Execute the graph from its entrypoint using initial_state.
        Supports:
        - sequential transitions via edges
        - conditional routing using EdgeConfig.condition_key, gte, lt, if_true, if_false
        - simple looping by pointing edges back to previous nodes
        """
        graph = self.get_graph(graph_id)

        run_id = str(uuid.uuid4())
        run = Run(
            id=run_id,
            graph_id=graph_id,
            state=initial_state.copy(),
            log=[],
            status=RunStatus.PENDING,
            current_node=graph.entrypoint,
        )
        self.runs[run_id] = run
        run.status = RunStatus.RUNNING

        steps = 0
        current = graph.entrypoint

        while current is not None and steps < max_steps:
            node_cfg = graph.nodes[current]
            tool = tool_registry.get(node_cfg.tool)

            before_state = run.state.copy()
            try:
                result = tool(run.state)  # may modify state in-place and/or return updates
            except Exception as e:
                run.status = RunStatus.FAILED
                run.log.append(
                    {
                        "step": steps,
                        "node": current,
                        "error": str(e),
                        "state": run.state.copy(),
                    }
                )
                return run

            if result is not None:
                run.state.update(result)

            run.log.append(
                {
                    "step": steps,
                    "node": current,
                    "input": before_state,
                    "output": run.state.copy(),
                }
            )

            edge_cfg = graph.edges.get(current)
            if not edge_cfg:
                # No outgoing edge: stop.
                current = None
            else:
                # Default next
                next_node = edge_cfg.next

                # Optional conditional routing
                if edge_cfg.condition_key:
                    val = run.state.get(edge_cfg.condition_key)
                    condition_met = True

                    if edge_cfg.gte is not None:
                        condition_met = condition_met and (val is not None and val >= edge_cfg.gte)

                    if edge_cfg.lt is not None:
                        condition_met = condition_met and (val is not None and val < edge_cfg.lt)

                    if condition_met:
                        next_node = edge_cfg.if_true or next_node
                    else:
                        next_node = edge_cfg.if_false or next_node

                current = next_node

            run.current_node = current
            steps += 1

        if steps >= max_steps:
            run.status = RunStatus.FAILED
            run.log.append({"warning": "Max steps reached; possible infinite loop"})
        else:
            run.status = RunStatus.COMPLETED

        return run


engine = GraphEngine()
