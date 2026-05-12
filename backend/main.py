"""SmartContent AI — FastAPI entry point."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes import auth, generate, history

app = FastAPI(
    title="SmartContent AI",
    description="Generate and publish AI marketing content across platforms.",
    version="1.0.0",
)

# CORS — origines autorisées (local dev + Streamlit Cloud + env var pour prod).
# La variable d'env ALLOWED_ORIGINS accepte une liste séparée par virgules :
#   ALLOWED_ORIGINS="https://monapp.streamlit.app,https://www.monapp.com"
_default_origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:3000",
]
_env_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
_allow_origins = _default_origins + _env_origins

# Si rien n'est configuré pour la prod, on autorise les sous-domaines Streamlit Cloud par regex.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_origin_regex=r"https://.*\.streamlit\.app",
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
    # En prod (Railway), uvicorn est lancé via le Procfile avec $PORT.
    # Ici, c'est uniquement pour le développement local.
    port = int(os.environ.get("PORT", settings.app_port))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
