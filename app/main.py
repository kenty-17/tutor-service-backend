from fastapi import FastAPI
from app.routers import services
from app.database import get_connection

app=FastAPI(title="Tutor Service")
app.include_router(services.router)

@app.get("/health")
def health():
    with get_connection() as conn:
        conn.execute("select 1")
    return {"status":"ok"}

