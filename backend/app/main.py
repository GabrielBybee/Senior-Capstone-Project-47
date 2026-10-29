from fastapi import FastAPI

app = FastAPI(title="SecureCode Tutor API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
