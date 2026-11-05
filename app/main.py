from fastapi import FastAPI,  HTTPException, status
from pydantic import BaseModel, Field
from itertools import count

app=FastAPI(title="Tutor Service")

class ServiceCreate(BaseModel):
    name: str=Field(min_length=1, max_length=100)

class ServiceRead(BaseModel):
    id: int
    name: str

class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)

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

@app.get("/services/{service_id}")
async def get_service(service_id: int)->ServiceRead:
    service=services.get(service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")
    return service

@app.patch("/services/{service_id}")
async def update_service(service_id: int, data: ServiceUpdate)->ServiceRead:
    service=services.get(service_id)
    if service is None:
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")
    if data.name is not None:
        for other in services.values():
            if other.id!=service_id and other.name==data.name:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Услуга уже существует")
        service.name=data.name
    return service





@app.get("/health")
def health():
    return {"status":"ok"}

