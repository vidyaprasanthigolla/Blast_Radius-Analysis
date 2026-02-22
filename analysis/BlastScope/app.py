import os
import sqlite3
import uuid
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from parser import parse_directory
from graph_builder import build_graph, get_graph_data
from analyzer import analyze_blast_radius

app = FastAPI(title="BlastScope")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_FILE = "reports.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id TEXT PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

class AnalyzeRequest(BaseModel):
    repo_path: str
    change_intent: str
    changed_node_id: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "report_id": None})

@app.get("/report/{report_id}", response_class=HTMLResponse)
async def view_report(request: Request, report_id: str):
    return templates.TemplateResponse("index.html", {"request": request, "report_id": report_id})

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    nodes, edges = parse_directory(req.repo_path)
    G = build_graph(nodes, edges)
    analysis_result = analyze_blast_radius(G, req.change_intent, req.changed_node_id)
    
    if "error" in analysis_result:
        return JSONResponse(status_code=400, content=analysis_result)
        
    graph_elements = get_graph_data(G)
    
    response_data = {
        "graph_elements": graph_elements,
        "impact_analysis": analysis_result
    }
    
    # Save to SQLite
    report_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO reports (id, data) VALUES (?, ?)", (report_id, json.dumps(response_data)))
    conn.commit()
    conn.close()
    
    response_data["report_id"] = report_id
    return response_data

@app.get("/api/report/{report_id}")
async def get_report_data(report_id: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM reports WHERE id=?", (report_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return JSONResponse(status_code=404, content={"error": "Report not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
