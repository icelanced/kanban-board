from fastapi import FastAPI

app = FastAPI(title="KanbanBoard")


@app.get("/health")
def health():
    return {"status": "ok", "project": "KanbanBoard"}