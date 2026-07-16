from fastapi import FastAPI

app = FastAPI(
    title="Ithaka Backend",
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Backend initialized successfully",
    }
