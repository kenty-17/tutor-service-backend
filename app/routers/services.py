from fastapi import APIRouter, HTTPException, status
from app.schemas import ServiceCreate, ServiceRead, ServiceUpdate
from app.database import get_connection

router = APIRouter(prefix="/services", tags=["Услуги"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_service(data: ServiceCreate) -> ServiceRead:
    with get_connection() as conn:
        check_sql = "select service_id from services where name = %s"
        check_params = (data.name,)
        check_result = conn.execute(check_sql, check_params)
        existing = check_result.fetchone()

        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Услуга уже существует")

        insert_sql = "insert into services (name) values (%s) returning service_id, name"
        insert_params = (data.name,)
        insert_result = conn.execute(insert_sql, insert_params)
        row = insert_result.fetchone()
    return row


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
def update_service(service_id: int, data: ServiceUpdate) -> ServiceRead:
    with get_connection() as conn:
        find_sql = "select service_id, name from services where service_id = %s"
        find_params = (service_id,)
        find_result = conn.execute(find_sql, find_params)
        service = find_result.fetchone()

        if service is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")

        if data.name is None:
            return service
        
        check_sql = "select service_id from services where name = %s and service_id <> %s"
        check_params = (data.name, service_id)
        check_result = conn.execute(check_sql, check_params)
        existing = check_result.fetchone()

        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Услуга уже существует")
        
        update_sql = "update services set name = %s where service_id = %s returning service_id, name"
        update_params = (data.name, service_id)
        update_result = conn.execute(update_sql, update_params)
        row = update_result.fetchone()
    return row