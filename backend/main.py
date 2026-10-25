from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module

import service
from models import Employee, Review, ReviewCreate

get_tasks_router = import_module("01_get_tasks").router
create_task_router = import_module("02_create_task").router

app = FastAPI(title="Classroom Fullstack Assignment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_tasks_router)
app.include_router(create_task_router)


@app.get("/employees", response_model=list[Employee])
def get_employees():
    return service.list_employees()

@app.get("/reviews", response_model=list[Review])
def get_reviews(
    employee_id: int | None = None,
    period_id: int | None = None,
):
    return service.list_reviews(
        employee_id=employee_id,
        period_id=period_id,
    )


@app.get("/reviews/{review_id}", response_model=Review)
def get_review(review_id: int):
    review = service.get_review(review_id)

    if review is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    return review


@app.post("/reviews", response_model=Review, status_code=201)
def create_review(review: ReviewCreate):
    return service.create_review(review)