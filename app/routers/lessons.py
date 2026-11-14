from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_connection
from app.schemas import LessonCreate, LessonRead
from datetime import timedelta
from pydantic import AwareDatetime

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

        new_start = data.start_at
        new_end = data.start_at + timedelta(minutes=data.duration_min)

        overlap_sql = """
            select lesson_id, start_at, duration_min
            from lessons
            where start_at < %s
              and %s < start_at + duration_min * interval '1 minute'
              and status is distinct from 'Отменено'
              and status is distinct from 'Перенесено'
            limit 1
        """
        overlap_params = (new_end, new_start)
        overlap_result = conn.execute(overlap_sql, overlap_params)
        overlap = overlap_result.fetchone()

        if overlap is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Время пересекается с занятием {overlap['lesson_id']}"
            )

        insert_sql = "insert into lessons (student_id, start_at, duration_min) values (%s, %s, %s) returning *"
        insert_params = (data.student_id, data.start_at, data.duration_min)
        insert_result = conn.execute(insert_sql, insert_params)
        row = insert_result.fetchone()
    return row

@router.get("")
def list_lessons(
    date_from: AwareDatetime = Query(alias="from"),
    date_to: AwareDatetime = Query(alias="to")) -> list[LessonRead]:
    if date_from >= date_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Начало периода должно быть раньше конца")

    with get_connection() as conn:
        sql = "select * from lessons where start_at >= %s and start_at < %s and status is null order by start_at"
        params = (date_from, date_to)
        result = conn.execute(sql, params)
        rows = result.fetchall()
    return rows
