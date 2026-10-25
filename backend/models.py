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


class Employee(BaseModel):
    id: int
    employee_id: str
    name: str
    department: str | None = None
    email: str | None = None
    status: str | None = None

class ReviewCreate(BaseModel):
    employee_id: int
    period_id: int
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    comments: str | None = None


class Review(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    period_id: int
    period_name: str
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    average_rating: Decimal
    comments: str | None = None
    created_at: datetime | None = None
