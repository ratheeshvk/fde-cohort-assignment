"""Pydantic models — rename fields to match your final table."""

from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "todo"


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    created_at: datetime | None = None
