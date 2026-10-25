from fastapi import APIRouter

import repository
from models import Task

router = APIRouter()


@router.get("/tasks", response_model=list[Task])
def get_tasks():
    return repository.get_all_tasks()
