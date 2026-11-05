from fastapi import FastAPI,  HTTPException, status
from pydantic import BaseModel, Field
from itertools import count

app=FastAPI(title="Tutor Service")

class ServiceCreate(BaseModel):
    name: str=Field(min_length=1, max_length=100)

class ServiceRead(BaseModel):
    id: int
    name: str

services: dict[int,ServiceRead]={}
service_ids=count(start=1)

@app.post("/services", status_code=status.HTTP_201_CREATED)
async def create_service(data: ServiceCreate)->ServiceRead:
    for service in services.values():
        if service.name==data.name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Услуга уже существует")
    service=ServiceRead(id=next(service_ids),name=data.name)
    services[service.id]=service
    return service

@app.get("/services")
async def list_services()->list[ServiceRead]:
    return list(services.values())


@app.get("/health")
def health():
    return {"status":"ok"}

