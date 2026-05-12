"""SmartContent AI — Streamlit frontend (Tech SaaS violet theme).

Run:
    streamlit run frontend/app.py --server.port 8501
"""
from __future__ import annotations

import csv
import io
import os
from datetime import datetime

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_BASE = os.environ.get("SMARTCONTENT_API", "http://localhost:8001")
N8N_WEBHOOK = os.environ.get(
    "SMARTCONTENT_N8N", "http://localhost:5678/webhook/smartcontent-publish"
)

st.set_page_config(
    page_title="SmartContent AI",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Brand assets
# ---------------------------------------------------------------------------
PRIMARY = "#7c3aed"
PRIMARY_HOVER = "#6d28d9"
ACCENT = "#a78bfa"

LOGO_SVG = """
<svg width="220" height="48" viewBox="0 0 220 48" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
  </defs>
  <rect x="2" y="4" width="40" height="40" rx="10" fill="url(#lg)"/>
  <path d="M22 12 l3 8 8 2 -8 2 -3 8 -3 -8 -8 -2 8 -2 z" fill="white"/>
  <circle cx="32" cy="16" r="2" fill="white" opacity="0.9"/>
  <circle cx="13" cy="32" r="1.5" fill="white" opacity="0.7"/>
  <text x="52" y="22" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
        font-size="17" font-weight="700" fill="#fafafa">SmartContent</text>
  <text x="52" y="40" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
        font-size="13" font-weight="600" fill="#a78bfa" letter-spacing="1.5">A&#8201;I</text>
</svg>
""".strip()

GLOBAL_CSS = f"""
<style>
:root {{
  --sc-primary: {PRIMARY};
  --sc-primary-hover: {PRIMARY_HOVER};
  --sc-accent: {ACCENT};
}}
.block-container {{ padding-top: 2rem !important; }}
section[data-testid="stSidebar"] > div {{
  background: linear-gradient(180deg, #0e1117 0%, #161a26 100%);
}}
h1, h2, h3 {{ letter-spacing: -0.01em; }}
h1 {{ font-weight: 800; }}
button[kind="primary"], button[kind="primaryFormSubmit"] {{
  background: linear-gradient(135deg, var(--sc-accent) 0%, var(--sc-primary) 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
  transition: transform .12s ease, box-shadow .12s ease !important;
}}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {{
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
}}
button[kind="secondary"] {{
  border: 1px solid rgba(167, 139, 250, 0.4) !important;
  color: var(--sc-accent) !important;
}}
[data-baseweb="input"] input:focus, textarea:focus {{
  border-color: var(--sc-primary) !important;
}}
button[role="tab"][aria-selected="true"] {{
  color: var(--sc-accent) !important;
}}
[data-baseweb="tab-highlight"] {{ background-color: var(--sc-primary) !important; }}
[data-testid="stMetric"] {{
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(167, 139, 250, 0.04) 100%);
  border: 1px solid rgba(124, 58, 237, 0.18);
  border-radius: 12px;
  padding: 1rem;
}}
[data-testid="stMetricValue"] {{ color: var(--sc-accent) !important; font-weight: 700; }}
[data-testid="stAlert"] {{ border-radius: 10px; }}
code {{ color: var(--sc-accent); background: rgba(124, 58, 237, 0.1) !important; padding: 2px 6px; border-radius: 4px; }}
.sc-footer {{
  margin-top: 3rem;
  padding-top: 1.2rem;
  padding-bottom: 0.6rem;
  border-top: 1px solid rgba(255,255,255,0.08);
  text-align: center;
  font-size: 0.78rem;
  color: rgba(255,255,255,0.45);
}}
.sc-hero-tagline {{
  font-size: 1.15rem;
  color: var(--sc-accent);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}}
.sc-hero-sub {{
  color: rgba(255,255,255,0.7);
  margin-bottom: 2rem;
}}
</style>
"""


def inject_brand() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        '<div class="sc-footer">© 2026 SmartContent AI — Projet de fin d\'études '
        "AEC IA Appliquée, Collège Multihexa</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Référentiels
# ---------------------------------------------------------------------------
TONS = [
    "Professionnel", "Dynamique", "Viral", "Storytelling", "Luxe",
    "Humoristique", "Inspirant", "Éducatif", "Motivant", "Premium",
    "Minimaliste", "Jeune et tendance", "Émotionnel", "Corporate", "Haut de gamme",
]
OBJECTIFS = [
    "Vendre", "Attirer des clients", "Promouvoir une offre", "Engager",
    "Annoncer", "Informer", "Éduquer", "Divertir", "Générer des leads",
    "Obtenir des rendez-vous", "Augmenter la visibilité",
    "Faire connaître la marque", "Créer de la confiance",
    "Augmenter les abonnés", "Créer du trafic",
]
SECTEURS = [
    "Restaurant / Bar", "Garage automobile", "Lavage automobile",
    "Débosselage / Peinture", "Immobilier", "Coaching", "Beauté / Esthétique",
    "Salon de coiffure", "Spa / Bien-être", "E-commerce", "Santé / Clinique",
    "Dentiste", "Finance", "Assurance", "Construction", "Architecture",
    "Nettoyage", "Transport", "Logistique", "Événementiel", "Agence marketing",
    "Créateur de contenu", "Photographie", "Mode / Vêtements", "Fitness / Gym",
    "Nutrition", "Éducation", "Formation en ligne", "Technologie", "Informatique",
    "Tourisme", "Hôtel / Auberge", "Location Airbnb", "Avocat / Juridique",
    "Animalerie", "Géomatique / Ingénierie", "Autre",
]
PLATEFORMES = [
    "LinkedIn", "Instagram", "Facebook", "TikTok", "YouTube Shorts",
    "X / Twitter", "Pinterest", "Threads", "Snapchat",
    "Google Business Profile", "Blog / Article SEO", "Email marketing",
]
TYPES_CONTENU = [
    "Post simple", "Carrousel Instagram", "Story Instagram", "Script vidéo",
    "Publicité", "Conseil / Astuce", "Avant / Après", "Storytelling",
    "Témoignage client", "Annonce événement", "Promotion limitée",
    "Présentation entreprise",
]
PLATFORM_SLUG = {
    "LinkedIn": "linkedin", "Instagram": "instagram", "Facebook": "facebook",
    "TikTok": "tiktok", "YouTube Shorts": "youtube_shorts",
    "X / Twitter": "x_twitter", "Pinterest": "pinterest", "Threads": "threads",
    "Snapchat": "snapchat", "Google Business Profile": "google_business",
    "Blog / Article SEO": "blog_seo", "Email marketing": "email",
}
SLUG_TO_DISPLAY = {v: k for k, v in PLATFORM_SLUG.items()}


def _slugify_platforms(display_names: list[str]) -> list[str]:
    return [PLATFORM_SLUG.get(n, n.lower().replace(" ", "_")) for n in display_names]


UPCOMING_FEATURES = [
    "Publication automatique", "Programmation des posts", "Génération vidéo IA",
    "Voix IA ElevenLabs", "Sous-titres automatiques", "Analyse des performances",
    "Gestion multi-entreprises", "Calendrier marketing IA",
    "Bibliothèque de modèles", "Suggestions IA automatiques",
]


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def _init_state() -> None:
    defaults = {
        "auth_token": None, "user_id": None, "user_email": None,
        "user_company": None, "user_plan": None,
        "last_generation": None, "page": "Connexion",
        "regen_data": None,
        "force_page": None,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


_init_state()


def _logged_in() -> bool:
    return bool(st.session_state.get("auth_token"))


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def _api(method: str, path: str, **kwargs):
    url = f"{API_BASE}{path}"
    timeout = kwargs.pop("timeout", 60)
    return requests.request(method, url, timeout=timeout, **kwargs)


def api_health() -> tuple[bool, str]:
    try:
        r = _api("GET", "/health", timeout=5)
        return r.ok, str(r.json()) if r.ok else f"HTTP {r.status_code}"
    except Exception as exc:
        return False, str(exc)


def api_register(email, password, company, plan):
    return _api("POST", "/auth/register", json={
        "email": email, "password": password,
        "nom_entreprise": company, "plan": plan,
    })


def api_login(email, password):
    return _api("POST", "/auth/login", json={"email": email, "password": password})


def api_generate(payload: dict):
    return _api("POST", "/generate/", json=payload, timeout=180)


def api_publish(payload: dict):
    return _api("POST", "/generate/publish", json=payload, timeout=60)


def api_history(user_id: str, statut: str | None = None, plateforme: str | None = None):
    params = {"limit": 100}
    if statut:
        params["statut"] = statut
    if plateforme:
        params["plateforme"] = plateforme
    return _api("GET", f"/history/{user_id}", params=params, timeout=30)


def api_delete_content(content_id: str):
    return _api("DELETE", f"/history/{content_id}", timeout=15)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(LOGO_SVG, unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        ok, info = api_health()
        if ok:
            st.success("● Backend en ligne")
        else:
            st.error(f"● Backend KO\n{info}")

        st.divider()
        if _logged_in():
            st.caption(f"👤 **{st.session_state.user_email}**")
            if st.session_state.user_company:
                st.caption(f"🏢 {st.session_state.user_company}")
            st.caption(f"⚡ Plan: **{st.session_state.user_plan or 'free'}**")
            pages = ["Générateur", "Tableau de bord", "Historique", "n8n Status", "Paramètres"]
        else:
            pages = ["Connexion"]

        # Force page from regen action (set before the radio renders)
        forced = st.session_state.pop("force_page", None)
        if forced and forced in pages:
            st.session_state["nav_radio"] = forced

        choice = st.radio("Navigation", pages, key="nav_radio", label_visibility="collapsed")

        if _logged_in():
            st.divider()
            if st.button("🚪 Déconnexion", use_container_width=True):
                for k in ["auth_token", "user_id", "user_email", "user_company", "user_plan", "last_generation"]:
                    st.session_state[k] = None
                st.rerun()

        st.divider()
        st.caption(f"API · `{API_BASE}`")
        st.caption(f"n8n · `{N8N_WEBHOOK}`")

    return choice


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_login() -> None:
    col_left, col_right = st.columns([1.1, 1])
    with col_left:
        st.markdown(LOGO_SVG, unsafe_allow_html=True)
        st.title("Bienvenue.")
        st.markdown('<div class="sc-hero-tagline">Créez. Automatisez. Publiez.</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sc-hero-sub">Génère du contenu marketing IA adapté à 12 plateformes — '
            'LinkedIn, Instagram, Facebook, TikTok, YouTube Shorts, et plus encore. '
            'Une idée, douze posts, en moins d\'une minute.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "**🪄 Génération multi-plateformes** · 12 réseaux sociaux  \n"
            "**🤖 IA GPT-4o** · ton, secteur, type de contenu personnalisés  \n"
            "**⚡ Publication automatique** · workflow n8n intégré  \n"
            "**📊 Tableau de bord** · suivi de tes contenus créés"
        )

    with col_right:
        tab_login, tab_register = st.tabs(["🔐  Connexion", "✨  Inscription"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="ton@email.com")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Se connecter", type="primary", use_container_width=True)
            if submit:
                try:
                    r = api_login(email, password)
                    if r.ok:
                        data = r.json()
                        st.session_state.update({
                            "auth_token": data["access_token"],
                            "user_id": data["user_id"],
                            "user_email": data["email"],
                            "user_company": data.get("nom_entreprise"),
                            "user_plan": data.get("plan", "free"),
                        })
                        st.success("Connecté ✅")
                        st.rerun()
                    else:
                        st.error(f"Échec : {r.status_code} — {r.text}")
                except Exception as exc:
                    st.error(f"Erreur réseau : {exc}")

        with tab_register:
            with st.form("register_form"):
                r_email = st.text_input("Email", key="r_email", placeholder="ton@email.com")
                r_password = st.text_input("Mot de passe (6+ caractères)", type="password", key="r_pw")
                r_company = st.text_input("Nom de l'entreprise (optionnel)", key="r_co", placeholder="Ex: Salon Élégance")
                r_plan = st.selectbox("Plan", ["free", "pro", "premium"], key="r_plan")
                submit_r = st.form_submit_button("Créer mon compte", type="primary", use_container_width=True)
            if submit_r:
                try:
                    r = api_register(r_email, r_password, r_company, r_plan)
                    if r.ok:
                        data = r.json()
                        st.session_state.update({
                            "auth_token": data["access_token"],
                            "user_id": data["user_id"],
                            "user_email": data["email"],
                            "user_company": data.get("nom_entreprise"),
                            "user_plan": data.get("plan", "free"),
                        })
                        st.success("Compte créé ✅")
                        st.rerun()
                    elif r.status_code == 409:
                        st.warning("Un compte existe déjà avec cet email.")
                    else:
                        st.error(f"Échec : {r.status_code} — {r.text}")
                except Exception as exc:
                    st.error(f"Erreur réseau : {exc}")


def page_generator() -> None:
    st.title("✨ Générateur de contenu")
    st.caption("Décris ton idée, choisis tes plateformes, l'IA génère et adapte automatiquement.")

    # Read regen data (set by the Historique page when user clicks "Modifier & régénérer")
    regen = st.session_state.get("regen_data") or {}
    if regen:
        st.info("✏️ **Mode régénération** — formulaire pré-rempli depuis un contenu existant. Modifie ce que tu veux puis clique Générer.")

    def _idx(opts: list[str], val: str | None, default: int = 0) -> int:
        try:
            return opts.index(val) if val in opts else default
        except Exception:
            return default

    default_sujet = regen.get("sujet", "")
    secteur_default = _idx(SECTEURS, regen.get("secteur"))
    ton_default = _idx(TONS, regen.get("ton"))
    objectif_default = _idx(OBJECTIFS, regen.get("objectif"))
    type_default = _idx(TYPES_CONTENU, regen.get("type_contenu"))
    regen_plats_slugs = set(regen.get("plateformes") or [])

    with st.form("gen_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            sujet = st.text_area(
                "Sujet / idée du post",
                value=default_sujet,
                height=140,
                placeholder="Ex: Lancement de notre nouvelle pizzeria napolitaine en plein cœur du Vieux-Montréal…",
            )
        with col2:
            secteur = st.selectbox("Secteur d'activité", SECTEURS, index=secteur_default)
            ton = st.selectbox("Ton souhaité", TONS, index=ton_default)
            objectif = st.selectbox("Objectif", OBJECTIFS, index=objectif_default)
            type_contenu = st.selectbox("Type de contenu", TYPES_CONTENU, index=type_default)

        st.markdown("**📡 Plateformes** (coche celles que tu veux)")
        plateformes_selected: list[str] = []
        cb_cols = st.columns(4)
        for idx, plat in enumerate(PLATEFORMES):
            col = cb_cols[idx % 4]
            slug = PLATFORM_SLUG[plat]
            if regen_plats_slugs:
                default_on = slug in regen_plats_slugs
            else:
                default_on = plat in ("LinkedIn", "Instagram", "Facebook", "TikTok")
            if col.checkbox(plat, value=default_on, key=f"plat_{plat}"):
                plateformes_selected.append(plat)

        submit = st.form_submit_button(
            "🚀 Générer mon contenu", type="primary", use_container_width=True
        )

    if submit:
        # Consume regen data (so next visit starts fresh)
        st.session_state.regen_data = None
        if not sujet.strip():
            st.warning("Entre un sujet.")
            return
        if not plateformes_selected:
            st.warning("Coche au moins une plateforme.")
            return
        plateformes_slugs = _slugify_platforms(plateformes_selected)
        with st.spinner("Génération en cours… (≈ 30-60 secondes par plateforme)"):
            try:
                r = api_generate({
                    "user_id": st.session_state.user_id,
                    "sujet": sujet,
                    "secteur": secteur,
                    "ton": ton,
                    "objectif": objectif,
                    "type_contenu": type_contenu,
                    "plateformes": plateformes_slugs,
                })
                if r.ok:
                    st.session_state.last_generation = r.json()
                    st.success("Contenu généré ✅")
                else:
                    st.error(f"Échec : {r.status_code} — {r.text}")
            except Exception as exc:
                st.error(f"Erreur : {exc}")

    gen = st.session_state.last_generation
    if not gen:
        return

    st.divider()
    st.subheader("📑 Résultats")
    content = gen.get("content", {})
    plat_results = content.get("plateformes", {})
    global_tags = content.get("hashtags_globaux", [])

    if plat_results:
        tabs = st.tabs([p.replace("_", " ").title() for p in plat_results.keys()])
        for tab, (name, data) in zip(tabs, plat_results.items()):
            with tab:
                if data.get("error"):
                    st.error(f"Erreur de génération: {data['error']}")
                    continue
                st.text_area(
                    f"Texte {name}",
                    data.get("texte", ""),
                    height=240,
                    key=f"txt_{hash(data.get('texte','')) % 100000}_{name}",
                )
                cols = st.columns(3)
                cols[0].metric("Mots", data.get("longueur_mots", 0))
                cols[1].metric("Hashtags", len(data.get("hashtags", [])))
                cols[2].metric("CTA", "✓" if data.get("cta") else "—")
                if data.get("cta"):
                    st.caption(f"**CTA :** {data['cta']}")
                if data.get("hashtags"):
                    st.write("**Hashtags :** " + " ".join(f"#{h.lstrip('#')}" for h in data["hashtags"]))

    if global_tags:
        st.write("---")
        st.write("**🌐 12 hashtags globaux :** " + " ".join(global_tags))

    # Images DALL-E (3 formats parallèles)
    images = content.get("images") or {}
    images_real = {k: v for k, v in images.items() if k != "errors" and isinstance(v, str)}
    if images_real:
        st.divider()
        st.subheader("🎨 Images générées par DALL-E 3")
        st.caption("Images générées par IA · URLs valides 60 minutes — télécharge-les si tu veux les conserver.")
        cols = st.columns(3)
        layout_map = [
            ("square", "Instagram / Facebook", "1:1"),
            ("landscape", "LinkedIn / Blog SEO", "16:9"),
            ("portrait", "TikTok / Reels / Stories", "9:16"),
        ]
        for col, (key, label, ratio) in zip(cols, layout_map):
            url = images_real.get(key)
            with col:
                if url:
                    st.image(url, use_container_width=True)
                    st.caption(f"**{label}** · {ratio}")
                    st.markdown(f"[📥 Télécharger]({url})")
                else:
                    st.info(f"Format {key} non disponible")
    elif images.get("errors"):
        st.warning(f"⚠️ Génération images partiellement échouée : {images.get('errors')}")

    st.divider()
    st.subheader("📤 Publier via n8n")
    if st.button("Envoyer au workflow n8n", type="primary"):
        with st.spinner("Envoi du webhook…"):
            try:
                r = api_publish({
                    "content_id": gen.get("id"),
                    "user_id": st.session_state.user_id,
                    "plateformes": list(plat_results.keys()),
                    "payload": content,
                })
                if r.ok:
                    st.success(f"Webhook OK — réponse: {r.json()}")
                else:
                    st.error(f"Échec : {r.status_code} — {r.text}")
            except Exception as exc:
                st.error(f"Erreur : {exc}")


def page_dashboard() -> None:
    st.title("📊 Tableau de bord")
    try:
        r = api_history(st.session_state.user_id)
        items = r.json() if r.ok else []
    except Exception as exc:
        st.error(f"Erreur : {exc}")
        items = []

    total = len(items)
    publies = sum(1 for it in items if it.get("statut") == "publie")
    drafts = total - publies
    plateformes_count: dict[str, int] = {}
    for it in items:
        for p in it.get("plateformes", []) or []:
            plateformes_count[p] = plateformes_count.get(p, 0) + 1

    c1, c2, c3 = st.columns(3)
    c1.metric("📝 Contenus créés", total)
    c2.metric("✅ Publiés", publies)
    c3.metric("📂 Drafts", drafts)

    if plateformes_count:
        st.subheader("📡 Répartition par plateforme")
        st.bar_chart(plateformes_count, color=PRIMARY)

    if items:
        st.subheader("🕒 5 derniers contenus")
        for it in items[:5]:
            st.write(f"• **{it.get('sujet', '(sans sujet)')}** — `{it.get('statut', 'draft')}` — {it.get('date_creation', '')}")

    st.divider()
    st.subheader("🚧 Fonctionnalités à venir")
    st.caption("En cours de développement — pas encore disponibles.")
    badge_css = (
        "<style>"
        ".sc-badge{display:inline-block;padding:6px 12px;margin:4px 6px 4px 0;"
        "border-radius:14px;background:rgba(124,58,237,0.08);color:#a78bfa;"
        "font-size:0.85rem;border:1px solid rgba(124,58,237,0.25);font-weight:500;}"
        "</style>"
    )
    badges_html = badge_css + "".join(
        f"<span class='sc-badge'>🔒 {feat}</span>" for feat in UPCOMING_FEATURES
    )
    st.markdown(badges_html, unsafe_allow_html=True)


def _build_history_csv(items: list[dict]) -> str:
    """Génère un CSV de l'historique."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "id", "sujet", "secteur", "ton", "objectif", "type_contenu",
        "plateformes", "statut", "date_creation",
    ])
    for it in items:
        writer.writerow([
            it.get("id", ""),
            it.get("sujet", ""),
            it.get("secteur", ""),
            it.get("ton", ""),
            it.get("objectif", ""),
            it.get("type_contenu", ""),
            ",".join(it.get("plateformes") or []),
            it.get("statut", ""),
            it.get("date_creation", ""),
        ])
    return buf.getvalue()


def page_history() -> None:
    st.title("📚 Historique")

    # Filtres
    fcol1, fcol2, fcol3 = st.columns([1.5, 1, 1])
    with fcol1:
        q = st.text_input("🔍 Recherche par mot-clé", "", placeholder="Tape un mot-clé du sujet…")
    with fcol2:
        statut_choice = st.selectbox("Filtre statut", ["Tous", "draft", "publie"], key="hist_filter_statut")
    with fcol3:
        plat_options = ["Toutes"] + list(PLATFORM_SLUG.values())
        plat_choice = st.selectbox(
            "Filtre plateforme",
            plat_options,
            format_func=lambda s: s if s == "Toutes" else SLUG_TO_DISPLAY.get(s, s),
            key="hist_filter_plat",
        )

    statut_param = None if statut_choice == "Tous" else statut_choice
    plateforme_param = None if plat_choice == "Toutes" else plat_choice

    try:
        r = api_history(st.session_state.user_id, statut=statut_param, plateforme=plateforme_param)
        items = r.json() if r.ok else []
    except Exception as exc:
        st.error(f"Erreur : {exc}")
        items = []

    if q:
        items = [it for it in items if q.lower() in (it.get("sujet") or "").lower()]

    # Top bar : compteur + export CSV
    bar_col1, bar_col2 = st.columns([3, 1])
    with bar_col1:
        st.caption(f"📊 **{len(items)}** contenu(s) trouvé(s)")
    with bar_col2:
        if items:
            csv_data = _build_history_csv(items)
            st.download_button(
                "📥 Export CSV",
                data=csv_data,
                file_name=f"smartcontent-historique-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    if not items:
        st.info("📭 Aucun contenu trouvé. Modifie les filtres ou crée ton premier post depuis le **Générateur**.")
        return

    st.divider()

    # Liste expansible
    for it in items:
        statut_icon = "✅" if it.get("statut") == "publie" else "📂"
        content_id = it.get("id") or ""
        with st.expander(f"📝 {it.get('sujet', '(sans sujet)')} — {statut_icon} {it.get('statut', 'draft')}"):
            st.caption(f"Créé le {it.get('date_creation', '')}")
            st.write(
                f"**Secteur :** {it.get('secteur')} | **Ton :** {it.get('ton')} | "
                f"**Objectif :** {it.get('objectif')} | **Type :** {it.get('type_contenu', '—')}"
            )
            content = it.get("content") or {}
            for plat, data in (content.get("plateformes") or {}).items():
                st.markdown(f"**{plat.replace('_', ' ').title()}**")
                st.write(data.get("texte", ""))

            # Actions
            st.divider()
            ac1, ac2, ac3 = st.columns([1.2, 1, 2.5])

            with ac1:
                if st.button("✏️ Modifier & régénérer", key=f"regen_{content_id}", use_container_width=True):
                    st.session_state.regen_data = {
                        "sujet": it.get("sujet", ""),
                        "secteur": it.get("secteur", ""),
                        "ton": it.get("ton", ""),
                        "objectif": it.get("objectif", ""),
                        "type_contenu": it.get("type_contenu", ""),
                        "plateformes": it.get("plateformes") or [],
                    }
                    st.session_state.force_page = "Générateur"
                    st.rerun()

            with ac2:
                confirm_key = f"confirm_del_{content_id}"
                if st.session_state.get(confirm_key):
                    if st.button("⚠️ Confirmer", key=f"del2_{content_id}", type="primary", use_container_width=True):
                        try:
                            r = api_delete_content(content_id)
                            if r.ok:
                                st.success("Supprimé ✅")
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
                            else:
                                st.error(f"Échec : {r.status_code} — {r.text}")
                        except Exception as exc:
                            st.error(f"Erreur : {exc}")
                else:
                    if st.button("🗑️ Supprimer", key=f"del_{content_id}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()

            with ac3:
                if st.session_state.get(f"confirm_del_{content_id}"):
                    st.caption("⚠️ Cliquer Confirmer pour supprimer définitivement (action irréversible).")


def page_n8n() -> None:
    st.title("⚡ n8n Status & Configuration")
    st.write(
        "n8n Desktop doit tourner sur **http://localhost:5678**.\n\n"
        "Le webhook est configuré sur :"
    )
    st.code(N8N_WEBHOOK, language="text")
    st.subheader("🧪 Test du webhook")
    if st.button("Envoyer un ping de test", type="primary"):
        try:
            r = api_publish({
                "content_id": None,
                "user_id": st.session_state.user_id,
                "plateformes": ["linkedin"],
                "payload": {"ping": True, "ts": datetime.utcnow().isoformat()},
            })
            if r.ok:
                st.success(f"OK — {r.json()}")
            else:
                st.error(f"{r.status_code} — {r.text}")
        except Exception as exc:
            st.error(f"Erreur : {exc}")

    st.divider()
    st.subheader("🛠 Étapes de configuration n8n")
    st.markdown(
        "1. Ouvre n8n Desktop et importe `n8n/smartcontent_workflow.json`.\n"
        "2. Active le workflow (clique **Publish**).\n"
        "3. En production, l'URL `/webhook/smartcontent-publish` est toujours active.\n"
        "4. Pour debug pas-à-pas, utiliser le mode `webhook-test/` + clic 'Listen for Test Event'."
    )


def page_settings() -> None:
    st.title("⚙️ Paramètres")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**👤 Utilisateur**")
        st.write(st.session_state.user_email)
        st.markdown("**🆔 ID**")
        st.code(st.session_state.user_id, language="text")
        st.markdown("**🏢 Entreprise**")
        st.write(st.session_state.user_company or "—")
    with col2:
        st.markdown("**⚡ Plan**")
        st.write(st.session_state.user_plan or "free")
        st.markdown("**🌐 API backend**")
        st.code(API_BASE, language="text")
        st.markdown("**🔌 n8n webhook**")
        st.code(N8N_WEBHOOK, language="text")

    st.info("ℹ️ Les modifications de paramètres seront ajoutées dans une prochaine version.")


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------
def main() -> None:
    inject_brand()
    page = render_sidebar()
    if not _logged_in():
        page_login()
        render_footer()
        return
    if page == "Générateur":
        page_generator()
    elif page == "Tableau de bord":
        page_dashboard()
    elif page == "Historique":
        page_history()
    elif page == "n8n Status":
        page_n8n()
    elif page == "Paramètres":
        page_settings()
    else:
        page_generator()
    render_footer()


if __name__ == "__main__":
    main()
