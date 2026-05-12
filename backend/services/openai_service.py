"""OpenAI service — multi-platform content + DALL-E 3 image generation."""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from openai import OpenAI

from backend.config import settings

_client = OpenAI(api_key=settings.openai_api_key)


# ===========================================================================
# TEXT PROMPTS
# ===========================================================================
PLATFORM_PROMPTS: dict[str, str] = {
    "linkedin": (
        "Rédige un post LinkedIn professionnel de 150 à 250 mots. "
        "Ton expert et engageant, structure claire (accroche, valeur, conclusion), "
        "termine par un CTA et 5 hashtags professionnels."
    ),
    "instagram": (
        "Rédige une légende Instagram de 80 à 150 mots. "
        "Ton inspirant, émojis pertinents, accroche forte sur la 1re ligne, "
        "termine par 10 à 15 hashtags pertinents."
    ),
    "facebook": (
        "Rédige un post Facebook de 100 à 200 mots, ton conversationnel et chaleureux. "
        "Termine par une question ouverte pour générer des commentaires, plus 3-5 hashtags."
    ),
    "tiktok": (
        "Rédige un script TikTok de 60 à 80 mots MAXIMUM. "
        "Format script parlé, rythme rapide, accroche en 3 secondes, "
        "5-8 hashtags tendance à la fin."
    ),
    "youtube_shorts": (
        "Rédige un script YouTube Shorts de 50 à 90 mots. "
        "Hook fort dans les 3 premières secondes, structure problème → solution → CTA, "
        "rythme rapide, 5-7 hashtags tendance."
    ),
    "x_twitter": (
        "Rédige un post X / Twitter de 240 à 280 caractères MAXIMUM (un seul tweet). "
        "Phrase percutante, ton direct, 2-4 hashtags ciblés."
    ),
    "pinterest": (
        "Rédige une description Pinterest de 100 à 200 caractères, "
        "orientée mots-clés SEO et inspiration visuelle. Ajoute 5-8 hashtags pertinents."
    ),
    "threads": (
        "Rédige un post Threads de 100 à 200 mots, ton conversationnel et authentique, "
        "comme une discussion entre amis. 3-5 hashtags."
    ),
    "snapchat": (
        "Rédige un texte court Snapchat de 30 à 60 mots, ton fun et spontané, "
        "émojis bienvenus, 3-5 hashtags trendy."
    ),
    "google_business": (
        "Rédige un post Google Business Profile de 100 à 250 mots, "
        "ton local et engageant, mots-clés SEO du secteur, CTA clair "
        "(appeler / réserver / visiter). Pas de hashtags."
    ),
    "blog_seo": (
        "Rédige une introduction d'article de blog SEO de 200 à 350 mots. "
        "Inclure un H1 et 2 sous-titres H2, mots-clés naturellement intégrés, "
        "ton informatif et structuré. 0 hashtag."
    ),
    "email": (
        "Rédige un email marketing de 150 à 250 mots, structure : "
        "objet accrocheur (préfixé 'Objet:'), accroche, valeur, CTA clair. "
        "Pas de hashtags."
    ),
}


CTA_BY_OBJECTIVE: dict[str, str] = {
    "Vendre": "Découvre l'offre maintenant 👉",
    "Attirer des clients": "Réserve ton appel découverte 📞",
    "Promouvoir une offre": "Profite de l'offre limitée ⏳",
    "Engager": "Dis-moi en commentaire ce que tu en penses 💬",
    "Annoncer": "Marque ton calendrier 📅",
    "Informer": "Lis l'article complet en commentaire 💡",
    "Éduquer": "Sauvegarde ce post pour plus tard 📌",
    "Divertir": "Partage avec un ami qui aimera 😄",
    "Générer des leads": "Inscris-toi en 30 secondes 🎯",
    "Obtenir des rendez-vous": "Prends rendez-vous en ligne 📆",
    "Augmenter la visibilité": "Partage si ça t'a plu 🔁",
    "Faire connaître la marque": "Suis-nous pour plus de contenu 🚀",
    "Créer de la confiance": "Découvre nos clients en commentaire 🤝",
    "Augmenter les abonnés": "Abonne-toi pour ne rien manquer 🔔",
    "Créer du trafic": "Clique sur le lien dans la bio 🔗",
    "vendre": "Découvre l'offre maintenant 👉",
    "informer": "Lis l'article complet en commentaire 💡",
    "annoncer": "Marque ton calendrier 📅",
    "eduquer": "Sauvegarde ce post pour plus tard 📌",
    "motiver": "Partage si tu es d'accord 💪",
}


def _system_prompt(secteur: str, ton: str, objectif: str, type_contenu: str) -> str:
    return (
        "Tu es un expert en marketing de contenu et copywriting multi-plateformes. "
        f"Secteur d'activité: {secteur}. Ton souhaité: {ton}. Objectif: {objectif}. "
        f"Type de contenu attendu: {type_contenu}. "
        "Réponds STRICTEMENT en JSON avec les clés: texte (str), hashtags (list[str]), cta (str). "
        "Pas d'explication hors JSON, pas de markdown, pas de balises code."
    )


def _extract_json(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {}


def _generate_one(
    platform: str, sujet: str, secteur: str, ton: str, objectif: str, type_contenu: str,
) -> dict[str, Any]:
    platform_brief = PLATFORM_PROMPTS.get(
        platform,
        f"Rédige un contenu marketing adapté à la plateforme '{platform}', "
        "ton naturel, longueur raisonnable, hashtags pertinents si la plateforme s'y prête.",
    )
    user_prompt = (
        f"{platform_brief}\n\n"
        f"Génère un '{type_contenu}' pour {platform}.\n"
        f"Sujet : {sujet}\n"
        f"Tu DOIS répondre en JSON: {{\"texte\": ..., \"hashtags\": [...], \"cta\": ...}}."
    )
    response = _client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": _system_prompt(secteur, ton, objectif, type_contenu)},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or ""
    data = _extract_json(raw)

    texte = data.get("texte") or data.get("text") or raw
    hashtags = data.get("hashtags") or []
    if isinstance(hashtags, str):
        hashtags = [h.strip() for h in re.findall(r"#\w+", hashtags)]
    cta = data.get("cta") or CTA_BY_OBJECTIVE.get(objectif, "")

    return {
        "plateforme": platform,
        "texte": texte.strip(),
        "hashtags": hashtags,
        "cta": cta,
        "longueur_mots": len(texte.split()) if texte else 0,
    }


def generate_global_hashtags(sujet: str, secteur: str) -> list[str]:
    prompt = (
        f"Donne-moi exactement 12 hashtags pertinents (sans le #) en JSON list "
        f"pour un contenu marketing sur: '{sujet}', secteur: {secteur}. "
        "Réponds en JSON: {\"hashtags\": [...]}"
    )
    try:
        response = _client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        data = _extract_json(response.choices[0].message.content or "")
        tags = data.get("hashtags", [])
        return [f"#{t.lstrip('#')}" for t in tags][:12]
    except Exception:
        return []


# ===========================================================================
# IMAGES (DALL-E 3)
# ===========================================================================
# 3 formats — adaptés aux plateformes:
#   square    1:1   1024x1024  → Instagram, Facebook feed
#   landscape 16:9  1792x1024  → LinkedIn, Facebook cover, Blog/SEO
#   portrait  9:16  1024x1792  → TikTok, Reels, Stories, Pinterest
IMAGE_FORMATS: list[tuple[str, str]] = [
    ("square", "1024x1024"),
    ("landscape", "1792x1024"),
    ("portrait", "1024x1792"),
]


def _build_image_prompt(sujet: str, secteur: str, ton: str) -> str:
    return (
        f"Professional marketing photo for {secteur} business. "
        f"Campaign: {sujet}. Tone: {ton}. "
        "High quality commercial photography. "
        "No text, no words, no letters in the image. "
        "Clean, professional, suitable for social media."
    )


def _generate_one_image(prompt: str, fmt: tuple[str, str]) -> tuple[str, str | None, str | None]:
    """Returns (format_name, url, error_or_none)."""
    name, size = fmt
    try:
        r = _client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        return name, r.data[0].url, None
    except Exception as exc:
        return name, None, str(exc)


def generate_images(sujet: str, secteur: str, ton: str) -> dict[str, Any]:
    """Génère 3 images DALL-E 3 (square, landscape, portrait) en parallèle.

    Renvoie:
        {
          "square": "https://...",
          "landscape": "https://...",
          "portrait": "https://...",
          "errors": {...}  # si certaines ont échoué
        }
    """
    prompt = _build_image_prompt(sujet, secteur, ton)
    out: dict[str, Any] = {}
    errors: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(_generate_one_image, prompt, fmt) for fmt in IMAGE_FORMATS]
        for f in futures:
            name, url, err = f.result()
            if url:
                out[name] = url
            if err:
                errors[name] = err
    if errors:
        out["errors"] = errors
    return out


# ===========================================================================
# ORCHESTRATION
# ===========================================================================
def generate_multi_platform(
    sujet: str,
    secteur: str = "general",
    ton: str = "professionnel",
    objectif: str = "informer",
    type_contenu: str = "Post simple",
    plateformes: list[str] | None = None,
    with_images: bool = True,
) -> dict[str, Any]:
    plateformes = plateformes or ["linkedin", "instagram", "facebook", "tiktok"]
    out: dict[str, Any] = {"plateformes": {}}

    # 1) Generate texts (sequential — could be parallel too, but keeps cost predictable)
    for p in plateformes:
        try:
            out["plateformes"][p] = _generate_one(p, sujet, secteur, ton, objectif, type_contenu)
        except Exception as exc:
            out["plateformes"][p] = {
                "plateforme": p,
                "error": str(exc),
                "texte": "",
                "hashtags": [],
                "cta": "",
                "longueur_mots": 0,
            }

    # 2) Global hashtags
    out["hashtags_globaux"] = generate_global_hashtags(sujet, secteur)
    out["cta_objectif"] = CTA_BY_OBJECTIVE.get(objectif, "")
    out["type_contenu"] = type_contenu

    # 3) Images (DALL-E 3 — 3 formats en parallèle, ~15-20s)
    if with_images:
        try:
            out["images"] = generate_images(sujet, secteur, ton)
        except Exception as exc:
            out["images"] = {"errors": {"global": str(exc)}}
    else:
        out["images"] = {}

    return out
