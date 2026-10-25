"""Pydantic models — rename fields to match your final table."""

from datetime import datetime

from pydantic import BaseModel, Field

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
    quality_rating: int = Field(ge=1, le=5)
    delivery_rating: int = Field(ge=1, le=5)
    teamwork_rating: int = Field(ge=1, le=5)
    comments: str | None = None


class Review(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    period_id: int
    period_name: str | None = None
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    average_rating: float
    comments: str | None = None
    created_at: datetime | None = None
