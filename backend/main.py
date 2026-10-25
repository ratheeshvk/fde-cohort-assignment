from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

import service
from models import Employee, Review, ReviewCreate

app = FastAPI(title="Classroom Fullstack Assignment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/employees", response_model=list[Employee])
def get_employees():
    return service.list_employees()


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: str = Path(..., min_length=1, max_length=20)):
    employee = service.get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post("/api/reviews", response_model=Review, status_code=201)
def create_review(review: ReviewCreate):
    return service.create_review(review)