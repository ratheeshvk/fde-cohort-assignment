from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module

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
