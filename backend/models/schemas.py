"""Pydantic schemas — request/response models."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# -------- Auth --------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nom_entreprise: Optional[str] = None
    plan: str = "free"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    nom_entreprise: Optional[str] = None
    plan: str


# -------- Generation --------
class GenerateRequest(BaseModel):
    user_id: Optional[str] = None
    sujet: str
    secteur: Optional[str] = "general"
    ton: Optional[str] = "professionnel"
    objectif: Optional[str] = "informer"
    type_contenu: Optional[str] = "Post simple"
    plateformes: list[str] = Field(
        default_factory=lambda: ["linkedin", "instagram", "facebook", "tiktok"]
    )


class PlatformContent(BaseModel):
    plateforme: str
    texte: str
    hashtags: list[str]
    cta: str
    longueur_mots: int


class GenerateResponse(BaseModel):
    id: Optional[str] = None
    sujet: str
    content: dict[str, Any]
    statut: str = "draft"
    date_creation: datetime = Field(default_factory=datetime.utcnow)


# -------- Publish (n8n) --------
class PublishRequest(BaseModel):
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    plateformes: list[str]
    payload: dict[str, Any]


class PublishResponse(BaseModel):
    ok: bool
    n8n_response: Any


# -------- History --------
class HistoryItem(BaseModel):
    id: str
    sujet: str
    secteur: Optional[str] = None
    ton: Optional[str] = None
    objectif: Optional[str] = None
    plateformes: list[str] = []
    statut: str = "draft"
    date_creation: Optional[str] = None
    content: Optional[dict[str, Any]] = None
