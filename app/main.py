from fastapi import FastAPI

app=FastAPI(title="Tutor Service")

@app.get("/health")
def health():
    return {"status":"ok"}

