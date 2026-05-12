"""SmartContent AI — FastAPI entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes import auth, generate, history

app = FastAPI(
    title="SmartContent AI",
    description="Generate and publish AI marketing content across platforms.",
    version="1.0.0",
)

# CORS — Streamlit runs on 8501, allow it (and a few common dev origins).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "app": "SmartContent AI",
        "version": "1.0.0",
        "env": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])
app.include_router(history.router, prefix="/history", tags=["history"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.app_port, reload=True)
