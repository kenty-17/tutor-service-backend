from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import LessonCreate, LessonRead

router = APIRouter(prefix="/lessons", tags=["Занятия"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_lesson(data: LessonCreate) -> LessonRead:
    with get_connection() as conn:
        student_sql = "select student_id, is_active from students where student_id = %s"
        student_params = (data.student_id,)
        student_result = conn.execute(student_sql, student_params)
        student = student_result.fetchone()

        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ученик не найден")

        if not student["is_active"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ученик в архиве")

        insert_sql = "insert into lessons (student_id, start_at, duration_min) values (%s, %s, %s) returning *"
        insert_params = (data.student_id, data.start_at, data.duration_min)
        insert_result = conn.execute(insert_sql, insert_params)
        row = insert_result.fetchone()
    return row