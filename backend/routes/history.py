"""History routes — list (with filters) + delete."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.models.schemas import HistoryItem
from backend.services.supabase_service import supabase_admin

router = APIRouter()


@router.get("/{user_id}", response_model=list[HistoryItem])
def get_history(
    user_id: str,
    limit: int = 100,
    statut: Optional[str] = Query(None, description="draft | publie | erreur"),
    plateforme: Optional[str] = Query(None, description="linkedin | instagram | facebook | tiktok | ..."),
):
    try:
        query = supabase_admin.table("contents").select("*").eq("user_id", user_id)
        if statut:
            query = query.eq("statut", statut)
        if plateforme:
            # plateformes is a JSONB array; "contains" matches arrays that include the value
            query = query.contains("plateformes", [plateforme])
        res = query.order("date_creation", desc=True).limit(limit).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Supabase error: {exc}")
    return res.data or []


@router.delete("/{content_id}")
def delete_content(content_id: str):
    """Supprime un contenu par son ID."""
    try:
        res = supabase_admin.table("contents").delete().eq("id", content_id).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Supabase delete error: {exc}")
    if not res.data:
        raise HTTPException(status_code=404, detail="Contenu introuvable.")
    return {"ok": True, "deleted_id": content_id}
