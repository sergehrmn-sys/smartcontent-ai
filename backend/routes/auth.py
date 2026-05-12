"""Auth routes — register / login (bcrypt direct + JWT).

Note: we use the `bcrypt` library directly (not passlib).
passlib 1.7.4 is incompatible with bcrypt >= 4.1 due to ValueError
raised on >72-byte passwords during its startup self-test.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import APIRouter, HTTPException, status
from jose import jwt

from backend.config import settings
from backend.models.schemas import LoginRequest, RegisterRequest, TokenResponse
from backend.services.supabase_service import supabase_admin

router = APIRouter()


def _hash_password(plain: str) -> str:
    # bcrypt only allows up to 72 bytes; truncate for safety.
    pw_bytes = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        pw_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


def _create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest):
    existing = (
        supabase_admin.table("users").select("id").eq("email", payload.email).execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe deja avec cet email.",
        )

    user_record = {
        "email": payload.email,
        "password_hash": _hash_password(payload.password),
        "nom_entreprise": payload.nom_entreprise,
        "plan": payload.plan or "free",
        "date_inscription": datetime.now(timezone.utc).isoformat(),
    }

    insert = supabase_admin.table("users").insert(user_record).execute()
    if not insert.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la creation du compte. Verifie que la table 'users' existe et que RLS est desactive.",
        )

    user = insert.data[0]
    token = _create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return TokenResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"],
        nom_entreprise=user.get("nom_entreprise"),
        plan=user.get("plan", "free"),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    res = (
        supabase_admin.table("users")
        .select("*")
        .eq("email", payload.email)
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

    user = res.data[0]
    if not _verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

    token = _create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return TokenResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"],
        nom_entreprise=user.get("nom_entreprise"),
        plan=user.get("plan", "free"),
    )
