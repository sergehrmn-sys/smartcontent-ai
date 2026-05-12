"""Generate routes — content + images creation + publish via n8n."""
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.models.schemas import (
    GenerateRequest,
    GenerateResponse,
    PublishRequest,
    PublishResponse,
)
from backend.services.openai_service import generate_multi_platform
from backend.services.supabase_service import supabase_admin

router = APIRouter()


@router.post("/", response_model=GenerateResponse)
def generate_content(payload: GenerateRequest):
    try:
        content = generate_multi_platform(
            sujet=payload.sujet,
            secteur=payload.secteur or "general",
            ton=payload.ton or "professionnel",
            objectif=payload.objectif or "informer",
            type_contenu=payload.type_contenu or "Post simple",
            plateformes=payload.plateformes,
            with_images=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {exc}")

    images_only = content.get("images") or {}

    record = {
        "user_id": payload.user_id,
        "sujet": payload.sujet,
        "secteur": payload.secteur,
        "ton": payload.ton,
        "objectif": payload.objectif,
        "type_contenu": payload.type_contenu,
        "plateformes": payload.plateformes,
        "content": content,           # JSONB blob (textes + hashtags + images)
        "images": images_only,        # JSONB column dédié pour requêtes rapides
        "statut": "draft",
        "date_creation": datetime.now(timezone.utc).isoformat(),
    }

    saved_id = None
    try:
        if payload.user_id:
            ins = supabase_admin.table("contents").insert(record).execute()
            if ins.data:
                saved_id = str(ins.data[0].get("id"))
    except Exception as exc:
        # Si la colonne images n'existe pas encore, retry sans elle
        try:
            record.pop("images", None)
            if payload.user_id:
                ins = supabase_admin.table("contents").insert(record).execute()
                if ins.data:
                    saved_id = str(ins.data[0].get("id"))
        except Exception:
            saved_id = None

    return GenerateResponse(
        id=saved_id,
        sujet=payload.sujet,
        content=content,
        statut="draft",
    )


@router.post("/publish", response_model=PublishResponse)
def publish_content(payload: PublishRequest):
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                settings.n8n_webhook_url,
                json={
                    "content_id": payload.content_id,
                    "user_id": payload.user_id,
                    "plateformes": payload.plateformes,
                    "payload": payload.payload,
                },
            )
        ok = 200 <= r.status_code < 300
        try:
            body = r.json()
        except Exception:
            body = r.text

        if ok and payload.content_id:
            try:
                supabase_admin.table("contents").update({"statut": "publie"}).eq(
                    "id", payload.content_id
                ).execute()
            except Exception:
                pass

        return PublishResponse(ok=ok, n8n_response=body)
    except httpx.RequestError as exc:
        msg = "Impossible de joindre n8n. Verifie que n8n Desktop tourne sur 5678. Detail: " + str(exc)
        raise HTTPException(status_code=502, detail=msg)
