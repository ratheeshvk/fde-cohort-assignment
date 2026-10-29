# add comments for every line of code
import os  # import os to read configuration from environment variables

from fastapi import APIRouter, Cookie, Depends, FastAPI, HTTPException, Path, Response  # import FastAPI framework, routing, cookie/dependency helpers, HTTPException for error handling, and Path for path parameters
from fastapi.middleware.cors import CORSMiddleware  # import CORSMiddleware for handling Cross-Origin Resource Sharing

import service  # import the service module which contains business logic
from models import AdminUser, Employee, LoginRequest, Review, ReviewCreate, ReviewPeriod  # import data models for type annotations and request/response validation

AUTH_COOKIE = "access_token"  # name of the httponly cookie that carries the login token

app = FastAPI(title="Classroom Fullstack Assignment")  # create an instance of FastAPI with a title

app.add_middleware(
    CORSMiddleware,  # add CORS middleware to the FastAPI app
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),  # explicit origins only: browsers reject "*" when cookies are sent
    allow_credentials=True,  # allow cookies and credentials to be included in requests
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)


def require_admin(access_token: str | None = Cookie(default=None)) -> AdminUser:  # dependency that only lets logged-in admins through
    admin = service.admin_from_token(access_token) if access_token else None  # decode the cookie's token, None if missing, invalid or expired
    if admin is None:  # no valid login
        raise HTTPException(status_code=401, detail="NOT_AUTHENTICATED")  # reject the request with 401
    return admin  # hand the logged-in admin to the route


auth_router = APIRouter(prefix="/api/auth", tags=["auth"])  # public router for login/logout/me
api = APIRouter(dependencies=[Depends(require_admin)])  # every route on this router requires a logged-in admin


@auth_router.post("/login", response_model=AdminUser)  # define a POST endpoint to log in
def login(credentials: LoginRequest, response: Response):  # username and password come in the request body
    admin, token = service.login(credentials)  # check the password hash and create the token (401 INVALID_CREDENTIALS on failure)
    response.set_cookie(
        key=AUTH_COOKIE,  # cookie name
        value=token,  # the signed JWT
        httponly=True,  # JavaScript can't read the cookie
        samesite="lax",  # not sent on cross-site POSTs
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",  # set COOKIE_SECURE=true once the site runs on HTTPS
        max_age=service.token_lifetime_minutes() * 60,  # cookie lives exactly as long as the token
    )
    return admin  # return the logged-in admin


@auth_router.post("/logout", status_code=204)  # define a POST endpoint to log out
def logout(response: Response):  # works even if the token has already expired
    response.delete_cookie(key=AUTH_COOKIE, httponly=True, samesite="lax")  # tell the browser to drop the cookie


@auth_router.get("/me", response_model=AdminUser)  # define a GET endpoint the frontend calls on page load
def me(admin: AdminUser = Depends(require_admin)):  # 401 if no one is logged in
    return admin  # return the logged-in admin


@api.get("/employees", response_model=list[Employee])  # define a GET endpoint to list all employees
def get_employees():
    return service.list_employees()  # call the service layer to get the list of employees


@api.get("/employees/{employee_id}", response_model=Employee)  # define a GET endpoint to get a specific employee by ID
def get_employee(employee_id: str = Path(..., min_length=1, max_length=20)):  # employee_id is a path parameter with validation
    employee = service.get_employee(employee_id)  # call the service layer to get the employee
    if employee is None:  # if employee not found, raise 404 error
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee  # return the employee data


@api.get("/review-periods", response_model=list[ReviewPeriod])  # define a GET endpoint to list all review periods
def get_review_periods():
    return service.list_review_periods()  # call the service layer to get the list of review periods


@api.get("/reviews", response_model=list[Review])  # define a GET endpoint to list reviews with optional filters
def get_reviews(
    employee_id: int | None = None,  # optional query parameter for employee ID
    period_id: int | None = None,  # optional query parameter for review period ID
):
    return service.list_reviews(
        employee_id=employee_id,  # pass employee_id to service layer
        period_id=period_id,  # pass period_id to service layer
    )


@api.get("/reviews/{review_id}", response_model=Review)  # define a GET endpoint to get a specific review by ID
def get_review(review_id: int):  # review_id is a path parameter
    review = service.get_review(review_id)  # call the service layer to get the review
    if review is None:  # if review not found, raise 404 error
        raise HTTPException(status_code=404, detail="Review not found")
    return review  # return the review data


@api.post("/api/reviews", response_model=Review, status_code=201)  # define a POST endpoint to create a new review
def create_review(review: ReviewCreate):  # review data is passed in the request body
    return service.create_review(review)  # call the service layer to create the review and return it


app.include_router(auth_router)  # register the public auth routes
app.include_router(api)  # register the protected routes
