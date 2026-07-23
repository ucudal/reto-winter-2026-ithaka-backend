import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.cohort_api import router as cohort_router
from app.api.health import router as health_router
from app.api.stage_api import router as stages_router

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
app.include_router(stages_router)
app.include_router(cohort_router)
