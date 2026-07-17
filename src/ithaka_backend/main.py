from fastapi import FastAPI

app = FastAPI()


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/health/ready", tags=["Health"])
async def readiness() -> dict[str, str]:
    return {"status": "ready"}