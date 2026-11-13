from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import StudentCreate, StudentRead

router = APIRouter(prefix="/students", tags=["Ученики"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate) -> StudentRead:
    with get_connection() as conn:
        service_sql = "select service_id from services where service_id = %s"
        service_params = (data.service_id,)
        service_result = conn.execute(service_sql, service_params)
        service = service_result.fetchone()

        if service is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")

        insert_sql = "insert into students (name, contact, service_id, cost_per_hour) values (%s, %s, %s, %s) returning student_id, name, contact, parent_id, service_id, cost_per_hour, is_active"
        insert_params = (data.name, data.contact, data.service_id, data.cost_per_hour)
        insert_result = conn.execute(insert_sql, insert_params)
        row = insert_result.fetchone()
    return row