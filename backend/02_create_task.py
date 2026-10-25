from fastapi import APIRouter

import repository
from models import Task, TaskCreate

router = APIRouter()


@router.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    return repository.create_task(task)
