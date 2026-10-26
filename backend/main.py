# add comments for every line of code
from fastapi import FastAPI, HTTPException, Path  # import FastAPI framework, HTTPException for error handling, and Path for path parameters
from fastapi.middleware.cors import CORSMiddleware  # import CORSMiddleware for handling Cross-Origin Resource Sharing

import service  # import the service module which contains business logic
from models import Employee, Review, ReviewCreate, ReviewPeriod  # import data models for type annotations and request/response validation

app = FastAPI(title="Classroom Fullstack Assignment")  # create an instance of FastAPI with a title

app.add_middleware(
    CORSMiddleware,  # add CORS middleware to the FastAPI app
    allow_origins=["*"],  # allow requests from any origin
    allow_credentials=True,  # allow cookies and credentials to be included in requests
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

@app.get("/employees", response_model=list[Employee])  # define a GET endpoint to list all employees
def get_employees():
    return service.list_employees()  # call the service layer to get the list of employees


@app.get("/employees/{employee_id}", response_model=Employee)  # define a GET endpoint to get a specific employee by ID
def get_employee(employee_id: str = Path(..., min_length=1, max_length=20)):  # employee_id is a path parameter with validation
    employee = service.get_employee(employee_id)  # call the service layer to get the employee
    if employee is None:  # if employee not found, raise 404 error
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee  # return the employee data


@app.get("/review-periods", response_model=list[ReviewPeriod])  # define a GET endpoint to list all review periods
def get_review_periods():
    return service.list_review_periods()  # call the service layer to get the list of review periods


@app.get("/reviews", response_model=list[Review])  # define a GET endpoint to list reviews with optional filters
def get_reviews(
    employee_id: int | None = None,  # optional query parameter for employee ID
    period_id: int | None = None,  # optional query parameter for review period ID
):
    return service.list_reviews(
        employee_id=employee_id,  # pass employee_id to service layer
        period_id=period_id,  # pass period_id to service layer
    )


@app.get("/reviews/{review_id}", response_model=Review)  # define a GET endpoint to get a specific review by ID
def get_review(review_id: int):  # review_id is a path parameter
    review = service.get_review(review_id)  # call the service layer to get the review
    if review is None:  # if review not found, raise 404 error
        raise HTTPException(status_code=404, detail="Review not found")
    return review  # return the review data


@app.post("/api/reviews", response_model=Review, status_code=201)  # define a POST endpoint to create a new review
def create_review(review: ReviewCreate):  # review data is passed in the request body
    return service.create_review(review)  # call the service layer to create the review and return it                       