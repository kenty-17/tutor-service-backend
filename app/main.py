from fastapi import FastAPI
from app.routers import services, students, lessons
from app.database import get_connection

app=FastAPI(title="Tutor Service")
app.include_router(services.router)
app.include_router(students.router)
app.include_router(lessons.router)

@app.get("/health")
def health():
    with get_connection() as conn:
        conn.execute("select 1")
    return {"status":"ok"}

