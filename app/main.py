import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.cohort_api import router as cohort_router
from app.api.health import router as health_router
from app.api.users_api import router as users_router
from app.api.auth_api import router as auth_router
from app.api.tutors_api import router as tutors_router
from app.api.stage_api import router as stages_router
from app.api.groups_api import router as groups_router
from app.api.dashboard_api import router as dashboard_router

app = FastAPI(
    title="Ithaka Backend",
    version="0.1.0",
)
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tutors_router)
app.include_router(stages_router)
app.include_router(cohort_router)
app.include_router(groups_router)
app.include_router(dashboard_router)