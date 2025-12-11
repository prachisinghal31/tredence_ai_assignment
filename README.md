🚀 Mini Workflow Engine (Tredence Assignment)
=============================================

A lightweight, LangGraph-style workflow engine built with **FastAPI**.Nodes are simple Python functions, state flows between nodes, and edges define transitions—including branching and loops.

This project uses the **Code Review Mini-Agent** workflow as the demo pipeline.

📦 Features Your Engine Supports
================================

### ✅ 1. Nodes

Each node is a Python function (“tool”) that receives a shared state: dict and returns updates to merge into it.

### ✅ 2. Shared State

A single state dictionary flows across all nodes.Each node reads + writes keys to drive the workflow.

### ✅ 3. Edges & Transitions

Edges define which node runs next.Supports:

*   simple next-node (next)
    
*   conditional routing (condition\_key, gte, lt, if\_true, if\_false)
    

### ✅ 4. Looping

The workflow can loop back to a previous node.A safety limit (max\_steps) prevents infinite loops.

### ✅ 5. Clean API Endpoints

MethodEndpointDescriptionPOST/graph/createCreate a workflow graphPOST/graph/runExecute the graph synchronouslyGET/graph/state/{run\_id}Inspect the final state of a run

Swagger UI: [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

🧪 Example Workflow (Code Review Mini-Agent)
============================================

This demo workflow processes Python code using 5 rule-based steps:

1.  **Extract functions**
    
2.  **Check complexity**
    
3.  **Detect issues**
    
4.  **Suggest improvements**
    
5.  **Loop until quality\_score >= threshold**
    

It demonstrates:

*   State-based transitions
    
*   Multi-node execution
    
*   Looping logic
    
*   Deterministic rule-based scoring
    

▶️ How to Run the Project
=========================

### **1️⃣ Install dependencies**

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install -r requirements.txt   `

### **2️⃣ Start the FastAPI server**

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   uvicorn app.main:app --reload   `

### **3️⃣ Open the API documentation**

Visit:

👉 [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

From here you can:

*   Create a graph
    
*   Run the workflow
    
*   Inspect run state
    

### **4️⃣ Use the default workflow**

The root endpoint shows the pre-built graph ID:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   GET http://127.0.0.1:8000/   `

🛠 What I Would Improve With More Time
======================================

### ✦ 1. Asynchronous Execution + Background Workers

Reintroduce async tools and WebSocket streaming so long-running steps don’t block the API.

### ✦ 2. Persistence Layer

Add SQLite/Postgres persistence for:

*   graphs
    
*   runs
    
*   logs
    

This would survive server restarts and support history lookups.

### ✦ 3. Web UI for Visualizing Runs

A small React UI to show:

*   the graph structure
    
*   live state updates
    
*   step-by-step logs
    

### ✦ 4. Validation & Error Reporting

Improve validation of:

*   missing nodes
    
*   invalid edges
    
*   unreachable graph states
    

Better error messages → smoother debugging.

### ✦ 5. Graph Visualization

Auto-render DAG/flowchart from nodes + edges for easy understanding.

✔️ Summary
==========

This project demonstrates:

*   clear separation of engine, tools, and API layers
    
*   clean state-driven workflow logic
    
*   conditional transitions + loop support
    
*   easy-to-use synchronous API
    
*   a complete sample workflow (Code Review Agent)
