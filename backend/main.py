from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module

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


@app.post("/api/reviews", response_model=Review, status_code=201)
def create_review(review: ReviewCreate):
    return service.create_review(review)