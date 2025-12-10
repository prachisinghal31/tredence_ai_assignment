# app/tools.py
from typing import Dict, Any, List
from .graph_engine import tool_registry, NodeConfig, EdgeConfig, engine


# ---------- Tool implementations ----------

def extract_functions_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very naive function extractor: looks for 'def <name>(' patterns.
    Input: state["code"] : str
    Output: state["functions"] : List[str]
    """
    code = state.get("code", "")
    functions: List[str] = []

    for part in code.split("def "):
        if not part.strip():
            continue
        header = part.split("(", 1)[0]
        name = header.strip()
        if name:
            functions.append(name)

    return {"functions": functions}


def check_complexity_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Toy complexity metric based on number of functions.
    Output: state["complexity_score"] : float
    """
    functions: List[str] = state.get("functions", [])
    complexity_score = float(len(functions))
    return {"complexity_score": complexity_score}


def detect_issues_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Basic issue detection using simple heuristics.
    - Flags TODO comments
    - Flags print() usage as 'debug prints'
    """
    code = state.get("code", "")
    issues: List[str] = []

    if "TODO" in code:
        issues.append("Unresolved TODO comment found.")
    if "print(" in code:
        issues.append("Debug print statement found.")

    return {"issues": issues, "issue_count": len(issues)}


def suggest_improvements_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a list of improvement suggestions based on issues/complexity.
    """
    suggestions: List[str] = []
    issue_count = state.get("issue_count", 0)
    complexity_score = state.get("complexity_score", 0.0)

    if complexity_score > 5:
        suggestions.append("Consider splitting the module into smaller, focused components.")
    if issue_count > 0:
        suggestions.append("Resolve the detected issues before merging.")
    if not suggestions:
        suggestions.append("Code looks clean. Consider minor refactoring and docstring improvements.")

    return {"suggestions": suggestions}


def evaluate_quality_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produces a synthetic quality_score in [0, 1].
    Lower issues + lower complexity => higher quality.
    """
    issue_count = state.get("issue_count", 0)
    complexity = state.get("complexity_score", 0.0)

    raw_penalty = issue_count + complexity / 10.0
    quality = max(0.0, 1.0 - min(raw_penalty / 10.0, 1.0))
    state["quality_score"] = quality  # also store in-place
    return {"quality_score": quality}


# Register tools in the global registry
tool_registry.register("extract_functions", extract_functions_tool)
tool_registry.register("check_complexity", check_complexity_tool)
tool_registry.register("detect_issues", detect_issues_tool)
tool_registry.register("suggest_improvements", suggest_improvements_tool)
tool_registry.register("evaluate_quality", evaluate_quality_tool)


# ---------- Helper: build the default Code Review graph ----------

def create_default_code_review_graph() -> str:
    """
    Creates a sample graph for:
    1. Extract functions
    2. Check complexity
    3. Detect basic issues
    4. Suggest improvements
    5. Loop until quality_score >= threshold
    Returns: graph_id
    """
    nodes = {
        "extract": NodeConfig(tool="extract_functions"),
        "complexity": NodeConfig(tool="check_complexity"),
        "issues": NodeConfig(tool="detect_issues"),
        "improve": NodeConfig(tool="suggest_improvements"),
        "score": NodeConfig(tool="evaluate_quality"),
    }

    edges = {
        "extract": EdgeConfig(next="complexity"),
        "complexity": EdgeConfig(next="issues"),
        "issues": EdgeConfig(next="improve"),
        "improve": EdgeConfig(next="score"),
        # Loop: if quality_score < 0.8, go back to "improve"
        "score": EdgeConfig(
            condition_key="quality_score",
            gte=0.8,          # condition: quality_score >= 0.8
            if_true=None,     # stop if high quality
            if_false="improve"  # otherwise loop back
        ),
    }

    graph = engine.create_graph(nodes=nodes, edges=edges, entrypoint="extract")
    return graph.id


# Optionally: create this graph at import time and store its ID
DEFAULT_CODE_REVIEW_GRAPH_ID = create_default_code_review_graph()
