"""Email service — send marketing campaign via Resend."""
import os
from typing import Any

import resend


resend.api_key = os.environ.get("RESEND_API_KEY", "")

# Sender — utilise le domaine de test Resend (onboarding@resend.dev) tant qu'aucun
# domaine custom n'est vérifié. Une fois un domaine perso ajouté dans Resend,
# remplacer par "SmartContent AI <hello@tondomaine.com>".
FROM_DEFAULT = os.environ.get(
    "RESEND_FROM",
    "SmartContent AI <onboarding@resend.dev>",
)

# Libellé + couleur brand par plateforme (utilisé dans le template HTML)
PLATFORM_LABELS: dict[str, tuple[str, str]] = {
    "linkedin":        ("LinkedIn",         "0A66C2"),
    "instagram":       ("Instagram",        "E1306C"),
    "facebook":        ("Facebook",         "1877F2"),
    "tiktok":          ("TikTok",           "00B0B9"),
    "youtube_shorts":  ("YouTube Shorts",   "FF0000"),
    "x_twitter":       ("X / Twitter",      "111111"),
    "pinterest":       ("Pinterest",        "E60023"),
    "threads":         ("Threads",          "111111"),
    "snapchat":        ("Snapchat",         "C5B500"),
    "google_business": ("Google Business",  "4285F4"),
    "blog_seo":        ("Blog SEO",         "7C3AED"),
    "email":           ("Email marketing",  "475569"),
}


def _esc(text: str) -> str:
    """Échappe le HTML pour les contenus utilisateur."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_email_html(sujet: str, content: dict[str, Any], images: dict[str, Any]) -> str:
    """Construit le HTML d'email avec les 12 plateformes + 3 images IA."""
    plateformes = content.get("plateformes", {}) or {}
    global_tags = content.get("hashtags_globaux", []) or []

    parts: list[str] = []
    parts.append(f"""\
<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"/><title>SmartContent AI — Campagne</title></head>
<body style="margin:0;padding:0;background:#f4f4f7;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1f2937;">
<div style="max-width:720px;margin:0 auto;padding:24px;">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#7c3aed 0%,#a78bfa 100%);padding:36px 28px;border-radius:18px;text-align:center;color:#ffffff;">
    <div style="font-size:28px;font-weight:800;letter-spacing:0.3px;">✨ SmartContent AI</div>
    <div style="margin-top:8px;font-size:14px;opacity:0.9;">Ta campagne marketing est prête</div>
  </div>

  <!-- Sujet -->
  <div style="background:#ffffff;padding:24px 24px 8px 24px;margin-top:18px;border-radius:14px;border:1px solid #e5e7eb;">
    <div style="font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">CAMPAGNE</div>
    <h1 style="margin:6px 0 0 0;font-size:22px;color:#111827;font-weight:700;line-height:1.35;">{_esc(sujet)}</h1>
  </div>

  <!-- Plateformes -->
  <div style="margin-top:8px;">
""")

    for slug, data in plateformes.items():
        if not isinstance(data, dict):
            continue
        label, color = PLATFORM_LABELS.get(slug, (slug.replace("_", " ").title(), "7C3AED"))
        texte = (data.get("texte") or "").strip()
        cta = (data.get("cta") or "").strip()
        hashtags = data.get("hashtags") or []

        chips = ""
        if hashtags:
            chips_html = " ".join(
                f'<span style="display:inline-block;padding:3px 9px;margin:2px 4px 2px 0;border-radius:99px;background:#f3e8ff;color:#7c3aed;font-size:12px;font-weight:600;">#{_esc(str(h).lstrip("#"))}</span>'
                for h in hashtags
            )
            chips = f'<div style="margin-top:14px;">{chips_html}</div>'

        cta_block = ""
        if cta:
            cta_block = f"""\
    <div style="margin-top:14px;padding:12px 14px;background:#faf5ff;border-left:3px solid #{color};border-radius:8px;">
      <span style="display:inline-block;padding:2px 8px;background:#{color};color:#ffffff;font-size:10px;font-weight:800;letter-spacing:1.2px;border-radius:5px;">CTA</span>
      <span style="margin-left:8px;color:#1f2937;font-weight:500;">{_esc(cta)}</span>
    </div>"""

        parts.append(f"""\
    <div style="background:#ffffff;padding:22px 24px;margin-top:12px;border-radius:14px;border:1px solid #e5e7eb;border-left:4px solid #{color};">
      <div style="font-size:11px;color:#{color};text-transform:uppercase;letter-spacing:2px;font-weight:800;">{_esc(label)}</div>
      <div style="margin-top:10px;font-size:14px;line-height:1.65;color:#1f2937;white-space:pre-wrap;">{_esc(texte) or '<em style="color:#9ca3af;">Aucun texte généré.</em>'}</div>
      {cta_block}
      {chips}
    </div>
""")

    parts.append("  </div>\n")

    # Hashtags globaux
    if global_tags:
        tags_html = " ".join(_esc(str(h)) for h in global_tags)
        parts.append(f"""\
  <div style="background:#ffffff;padding:18px 22px;margin-top:14px;border-radius:12px;border:1px solid #e5e7eb;">
    <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">🌐 Hashtags globaux</div>
    <div style="margin-top:8px;color:#7c3aed;font-weight:500;font-size:13px;line-height:1.6;">{tags_html}</div>
  </div>
""")

    # Images DALL-E
    if images:
        real_urls = {k: v for k, v in images.items() if isinstance(v, str) and v.startswith("http")}
        if real_urls:
            parts.append("""\
  <div style="margin-top:24px;">
    <h2 style="margin:0 0 12px 0;font-size:18px;color:#111827;">🎨 Images IA générées</h2>
    <p style="margin:0 0 16px 0;font-size:13px;color:#6b7280;">URLs valides 60 minutes — télécharge-les rapidement pour les conserver.</p>
""")
            label_map = {
                "square":    ("Carré 1:1",    "Instagram / Facebook"),
                "landscape": ("Paysage 16:9", "LinkedIn / Blog SEO"),
                "portrait":  ("Portrait 9:16","TikTok / Reels / Stories"),
            }
            for key, url in real_urls.items():
                title, sub = label_map.get(key, (key.title(), ""))
                parts.append(f"""\
    <div style="background:#ffffff;padding:14px;margin-top:10px;border-radius:12px;border:1px solid #e5e7eb;text-align:center;">
      <img src="{_esc(url)}" alt="{_esc(title)}" style="max-width:100%;border-radius:10px;display:block;margin:0 auto;"/>
      <div style="margin-top:10px;font-size:13px;font-weight:600;color:#1f2937;">{_esc(title)}</div>
      <div style="font-size:11px;color:#6b7280;">{_esc(sub)}</div>
      <div style="margin-top:8px;"><a href="{_esc(url)}" style="display:inline-block;padding:8px 16px;background:#7c3aed;color:#ffffff;font-weight:600;font-size:13px;text-decoration:none;border-radius:8px;">📥 Télécharger</a></div>
    </div>
""")
            parts.append("  </div>\n")

    # Footer
    parts.append("""\
  <div style="margin-top:28px;padding:20px;text-align:center;color:#6b7280;font-size:12px;">
    <p style="margin:0 0 6px 0;">Généré par <a href="https://smartcontent-ai.streamlit.app" style="color:#7c3aed;text-decoration:none;font-weight:600;">SmartContent AI</a></p>
    <p style="margin:0;opacity:0.8;">Projet de fin d'études — AEC Intelligence Artificielle Appliquée — Collège Multihexa</p>
  </div>

</div>
</body>
</html>
""")

    return "".join(parts)


def send_campaign_email(
    to_email: str,
    sujet: str,
    content: dict[str, Any],
    images: dict[str, Any],
) -> dict[str, Any]:
    """Envoie un email avec la campagne complète via Resend."""
    if not resend.api_key:
        return {"ok": False, "error": "RESEND_API_KEY non configuré côté serveur."}

    try:
        html_body = build_email_html(sujet, content, images)
        subject = f"✨ Ta campagne : {sujet[:80]}"
        params: dict[str, Any] = {
            "from": FROM_DEFAULT,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        result = resend.Emails.send(params)
        return {
            "ok": True,
            "id": result.get("id") if isinstance(result, dict) else None,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
