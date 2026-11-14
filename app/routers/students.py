from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import StudentCard, StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["Ученики"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate) -> StudentRead:
    if data.parent_id is not None and data.parent is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите либо parent_id, либо parent, но не и то, и другое"
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

@router.get("/{student_id}")
def get_student(student_id: int) -> StudentCard:
    with get_connection() as conn:
        sql = """
            select
                students.student_id,
                students.name,
                students.contact,
                students.is_active,
                students.cost_per_hour,
                services.service_id,
                services.name as service_name,
                parents.parent_id,
                parents.name as parent_name,
                parents.contact as parent_contact
            from students
            join services on services.service_id = students.service_id
            left join parents on parents.parent_id = students.parent_id
            where students.student_id = %s
        """
        params = (student_id,)
        result = conn.execute(sql, params)
        row = result.fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ученик не найден")
    return row

@router.patch("/{student_id}")
def update_student(student_id: int, data: StudentUpdate) -> StudentRead:
    with get_connection() as conn:
        find_sql = "select * from students where student_id = %s"
        find_params = (student_id,)
        find_result = conn.execute(find_sql, find_params)
        current = find_result.fetchone()

        if current is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ученик не найден")

        name = current["name"]
        if data.name is not None:
            name = data.name

        contact = current["contact"]
        if data.contact is not None:
            contact = data.contact

        service_id = current["service_id"]
        if data.service_id is not None:
            service_id = data.service_id

        cost_per_hour = current["cost_per_hour"]
        if data.cost_per_hour is not None:
            cost_per_hour = data.cost_per_hour

        parent_id = current["parent_id"]
        if data.parent_id is not None:
            parent_id = data.parent_id

        if data.service_id is not None:
            service_sql = "select service_id from services where service_id = %s"
            service_params = (data.service_id,)
            service_result = conn.execute(service_sql, service_params)
            if service_result.fetchone() is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")

        if data.parent_id is not None:
            parent_sql = "select parent_id from parents where parent_id = %s"
            parent_params = (data.parent_id,)
            parent_result = conn.execute(parent_sql, parent_params)
            if parent_result.fetchone() is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Родитель не найден")

        update_sql = """
            update students
            set name = %s, contact = %s, service_id = %s, cost_per_hour = %s, parent_id = %s
            where student_id = %s
            returning *
        """
        update_params = (name, contact, service_id, cost_per_hour, parent_id, student_id)
        update_result = conn.execute(update_sql, update_params)
        row = update_result.fetchone()
    return row

@router.post("/{student_id}/archive")
def archive_student(student_id: int) -> StudentRead:
    with get_connection() as conn:
        sql = "update students set is_active = false where student_id = %s returning *"
        params = (student_id,)
        result = conn.execute(sql, params)
        row = result.fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ученик не найден")
    return row
