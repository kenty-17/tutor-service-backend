from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import StudentCreate, StudentRead

router = APIRouter(prefix="/students", tags=["Ученики"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate) -> StudentRead:
    if data.parent_id is not None and data.parent is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите либо parent_id, либо parent, но не и то, и другое",
        )

    with get_connection() as conn:
        service_sql = "select service_id from services where service_id = %s"
        service_params = (data.service_id,)
        service_result = conn.execute(service_sql, service_params)
        service = service_result.fetchone()

        if service is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")
        parent_id = data.parent_id

        if data.parent_id is not None:
            parent_sql = "select parent_id from parents where parent_id = %s"
            parent_params = (data.parent_id,)
            parent_result = conn.execute(parent_sql, parent_params)
            parent = parent_result.fetchone()

            if parent is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Родитель не найден")

        elif data.parent is not None:
            new_parent_sql = "insert into parents (name, contact) values (%s, %s) returning parent_id"
            new_parent_params = (data.parent.name, data.parent.contact)
            new_parent_result = conn.execute(new_parent_sql, new_parent_params)
            new_parent = new_parent_result.fetchone()
            parent_id = new_parent["parent_id"]

        insert_sql = "insert into students (name, contact, parent_id, service_id, cost_per_hour) values (%s, %s, %s, %s, %s) returning *"
        insert_params = (data.name, data.contact, parent_id, data.service_id, data.cost_per_hour)
        insert_result = conn.execute(insert_sql, insert_params)
        row = insert_result.fetchone()
    return row

@router.get("")
def list_students(is_active: bool | None = None) -> list[StudentRead]:
    with get_connection() as conn:
        if is_active is None:
            sql = "select * from students order by student_id"
            params = ()
        else:
            sql = "select * from students where is_active = %s order by student_id"
            params = (is_active,)

        result = conn.execute(sql, params)
        rows = result.fetchall()
    return rows