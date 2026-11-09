from itertools import count
from fastapi import APIRouter, HTTPException, status
from app.schemas import ServiceCreate, ServiceRead, ServiceUpdate
from app.database import get_connection

router = APIRouter(prefix="/services", tags=["Услуги"])

services: dict[int, ServiceRead] = {}
service_ids = count(start=1)


def get_service_or_404(service_id: int) -> ServiceRead:
    service = services.get(service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")
    return service


def ensure_name_is_free(name: str, exclude_id: int | None = None) -> None:
    for other in services.values():
        if other.service_id != exclude_id and other.name == name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Услуга уже существует")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_service(data: ServiceCreate) -> ServiceRead:
    ensure_name_is_free(data.name)
    service = ServiceRead(service_id=next(service_ids), name=data.name)
    services[service.service_id] = service
    return service


@router.get("")
def list_services() -> list[ServiceRead]:
    with get_connection() as conn:
        rows=conn.execute("select service_id, name from services order by service_id").fetchall()
    return rows


@router.get("/{service_id}")
def get_service(service_id: int) -> ServiceRead:
    with get_connection() as conn:
        sql = "select service_id, name from services where service_id = %s"
        params = (service_id,)
        result = conn.execute(sql, params)
        row = result.fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")
    return row


@router.patch("/{service_id}")
async def update_service(service_id: int, data: ServiceUpdate) -> ServiceRead:
    service = get_service_or_404(service_id)
    if data.name is not None:
        ensure_name_is_free(data.name, exclude_id=service_id)
        service.name = data.name
    return service