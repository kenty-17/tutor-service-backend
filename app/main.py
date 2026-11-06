from fastapi import FastAPI
from app.routers import services

app=FastAPI(title="Tutor Service")
app.include_router(services.router)

@app.get("/health")
def health():
    return {"status":"ok"}

