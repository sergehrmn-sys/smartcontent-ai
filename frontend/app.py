"""SmartContent AI — Streamlit frontend (Tech SaaS violet theme).

Run:
    streamlit run frontend/app.py --server.port 8501
"""
from __future__ import annotations

import csv
import html as _html
import io
import os
from datetime import datetime

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# URL du backend FastAPI. En local : http://localhost:8001.
# En prod (Streamlit Cloud) : définir BACKEND_URL dans les Secrets Streamlit,
# ex. BACKEND_URL = "https://smartcontent-ai.up.railway.app".
# Compatibilité : on accepte aussi SMARTCONTENT_API (ancien nom) en fallback.
def _read_secret(*keys, default=""):
    for k in keys:
        v = os.environ.get(k)
        if v:
            return v
    try:
        for k in keys:
            if k in st.secrets:
                return st.secrets[k]
    except Exception:
        pass
    return default


API_BASE = _read_secret("BACKEND_URL", "SMARTCONTENT_API", default="http://localhost:8001").rstrip("/")
N8N_WEBHOOK = _read_secret("N8N_WEBHOOK_URL", "SMARTCONTENT_N8N",
                          default="http://localhost:5678/webhook/smartcontent-publish")

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

# ===========================================================================
# CSS MODULAIRE — chaque section est éditable indépendamment.
# Le rendu final concaténé est strictement identique à l'ancien GLOBAL_CSS.
# ===========================================================================

# --- Variables CSS (couleurs interpolées depuis Python) ---
_CSS_VARS = f"""
:root {{
  --sc-primary: {PRIMARY};
  --sc-primary-hover: {PRIMARY_HOVER};
  --sc-accent: {ACCENT};
}}
"""

# --- Layout général (padding, sidebar gradient) ---
_CSS_LAYOUT = """
.block-container { padding-top: 2rem !important; }
section[data-testid="stSidebar"] > div {
  background: linear-gradient(180deg, #0e1117 0%, #161a26 100%);
}
"""

# --- Typographie (titres) ---
_CSS_TYPOGRAPHY = """
h1, h2, h3 { letter-spacing: -0.01em; }
h1 { font-weight: 800; }
"""

# --- Boutons (primaire + secondaire + hover) ---
_CSS_BUTTONS = """
button[kind="primary"], button[kind="primaryFormSubmit"] {
  background: linear-gradient(135deg, var(--sc-accent) 0%, var(--sc-primary) 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
  transition: transform .12s ease, box-shadow .12s ease !important;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
}
button[kind="secondary"] {
  border: 1px solid rgba(167, 139, 250, 0.4) !important;
  color: var(--sc-accent) !important;
}
"""

# --- Inputs et onglets ---
_CSS_INPUTS_TABS = """
[data-baseweb="input"] input:focus, textarea:focus {
  border-color: var(--sc-primary) !important;
}
button[role="tab"][aria-selected="true"] {
  color: var(--sc-accent) !important;
}
[data-baseweb="tab-highlight"] { background-color: var(--sc-primary) !important; }
"""

# --- Cartes de métriques (Tableau de bord) ---
_CSS_METRICS = """
[data-testid="stMetric"] {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(167, 139, 250, 0.04) 100%);
  border: 1px solid rgba(124, 58, 237, 0.18);
  border-radius: 12px;
  padding: 1rem;
}
[data-testid="stMetricValue"] { color: var(--sc-accent) !important; font-weight: 700; }
"""

# --- Alertes et chips de code ---
_CSS_ALERTS_CODE = """
[data-testid="stAlert"] { border-radius: 10px; }
code { color: var(--sc-accent); background: rgba(124, 58, 237, 0.1) !important; padding: 2px 6px; border-radius: 4px; }
"""

# --- Footer + hero de la page Connexion ---
_CSS_FOOTER_HERO = """
.sc-footer {
  margin-top: 3rem;
  padding-top: 1.2rem;
  padding-bottom: 0.6rem;
  border-top: 1px solid rgba(255,255,255,0.08);
  text-align: center;
  font-size: 0.78rem;
  color: rgba(255,255,255,0.45);
}
.sc-hero-tagline {
  font-size: 1.15rem;
  color: var(--sc-accent);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}
.sc-hero-sub {
  color: rgba(255,255,255,0.7);
  margin-bottom: 2rem;
}
"""

# --- Sidebar premium (statut, carte user, navigation, déconnexion) ---
_CSS_SIDEBAR = """
/* === SIDEBAR PREMIUM === */
section[data-testid="stSidebar"] {
  border-right: 1px solid rgba(167, 139, 250, 0.10);
}

/* Backend status pill (en ligne) */
.sc-status-online {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #34d399;
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 500;
  margin: 8px 0 4px 0;
  box-sizing: border-box;
}
.sc-status-online::before {
  content: '';
  width: 8px; height: 8px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  animation: sc-pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}
/* Backend status pill (hors ligne) */
.sc-status-offline {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 0.85rem;
  margin: 8px 0 4px 0;
  box-sizing: border-box;
}
.sc-status-offline::before {
  content: '';
  width: 8px; height: 8px;
  background: #ef4444;
  border-radius: 50%;
  flex-shrink: 0;
}
@keyframes sc-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%     { opacity: 0.55; transform: scale(0.92); }
}

/* Carte utilisateur */
.sc-user-card {
  background: rgba(124, 58, 237, 0.05);
  border: 1px solid rgba(124, 58, 237, 0.14);
  border-radius: 12px;
  padding: 12px;
  margin: 14px 0 8px 0;
  font-size: 0.82rem;
}
.sc-user-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.82);
  margin: 4px 0;
  word-break: break-word;
}
.sc-user-icon {
  font-size: 0.95rem;
  flex-shrink: 0;
  width: 18px;
  text-align: center;
}
.sc-plan-badge {
  display: inline-block;
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-left: auto;
}

/* Navigation — style cards (radio buttons) */
section[data-testid="stSidebar"] [role="radiogroup"] {
  gap: 2px;
  margin-top: 4px;
}
section[data-testid="stSidebar"] [role="radiogroup"] label {
  padding: 9px 12px !important;
  border-radius: 9px !important;
  margin: 1px 0 !important;
  transition: background 0.15s ease, color 0.15s ease, border-left-color 0.15s ease !important;
  color: rgba(255, 255, 255, 0.65) !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  border-left: 3px solid transparent !important;
  cursor: pointer !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(124, 58, 237, 0.07) !important;
  color: rgba(255, 255, 255, 0.95) !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(167, 139, 250, 0.18) 0%, rgba(124, 58, 237, 0.06) 100%) !important;
  color: #ffffff !important;
  border-left: 3px solid #a78bfa !important;
}
/* Cache la pastille circulaire BaseWeb par défaut */
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-of-type {
  display: none !important;
}

/* Bouton Déconnexion — style ghost violet */
section[data-testid="stSidebar"] .stButton > button {
  background: rgba(124, 58, 237, 0.06) !important;
  border: 1px solid rgba(167, 139, 250, 0.30) !important;
  color: #c4b5fd !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  border-radius: 10px !important;
  padding: 8px 12px !important;
  transition: all 0.15s ease !important;
  box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(124, 58, 237, 0.18) !important;
  border-color: #7c3aed !important;
  color: #ffffff !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.25) !important;
}

/* Infos en bas (API + n8n URLs) */
.sc-info-bottom {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
}
.sc-info-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 4px 0;
}
.sc-info-row code {
  font-size: 0.62rem !important;
  padding: 1px 5px !important;
  word-break: break-all;
}
"""

# --- Layout premium (gradient body, hiérarchie titres, classes utilitaires, pill top) ---
_CSS_LAYOUT_PREMIUM = """
/* === FOND PRINCIPAL — DARK SAAS AVEC GRADIENT RADIAL VIOLET/BLEU === */
.stApp {
  background:
    radial-gradient(ellipse 80% 55% at 20% 0%, rgba(124, 58, 237, 0.08) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 90% 100%, rgba(59, 130, 246, 0.06) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 50% 50%, rgba(167, 139, 250, 0.03) 0%, transparent 70%),
    #0a0d14 !important;
  min-height: 100vh;
}
[data-testid="stAppViewContainer"] { background: transparent !important; }
.main .block-container { background: transparent !important; }

/* === HIÉRARCHIE TITRES === */
.main h1 {
  font-size: 2.2rem !important;
  font-weight: 800 !important;
  background: linear-gradient(120deg, #ffffff 0%, #c4b5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em !important;
  line-height: 1.15 !important;
  margin-bottom: 0.4rem !important;
}
.main h2 {
  font-size: 1.45rem !important;
  font-weight: 700 !important;
  color: #ffffff !important;
  letter-spacing: -0.01em !important;
  margin-top: 1.4rem !important;
  margin-bottom: 0.6rem !important;
}
.main h3 {
  font-size: 1.10rem !important;
  font-weight: 600 !important;
  color: rgba(255, 255, 255, 0.92) !important;
  margin-top: 1rem !important;
}
.main [data-testid="stCaptionContainer"] {
  color: rgba(255, 255, 255, 0.55) !important;
  font-size: 0.92rem !important;
}

/* === PASTILLE STATUT BACKEND (en haut à droite zone principale) === */
.sc-status-pill-top {
  position: fixed;
  top: 14px;
  right: 80px;
  z-index: 999;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(22, 26, 38, 0.70);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(16, 185, 129, 0.30);
  color: #34d399;
  padding: 5px 12px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 500;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.30);
  pointer-events: none;
  user-select: none;
}
.sc-status-pill-top.offline {
  border-color: rgba(239, 68, 68, 0.30);
  color: #f87171;
}
.sc-status-pill-top::before {
  content: '';
  width: 7px; height: 7px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 7px rgba(16, 185, 129, 0.7);
  animation: sc-pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}
.sc-status-pill-top.offline::before {
  background: #ef4444;
  box-shadow: 0 0 5px rgba(239, 68, 68, 0.5);
  animation: none;
}

/* === CLASSES UTILITAIRES GLOBALES === */

/* Carte glassmorphism (verre dépoli sombre) */
.glass-card {
  background: rgba(22, 26, 38, 0.55);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.18);
}

/* Carte premium (gradient violet subtil) */
.premium-card {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.10) 0%, rgba(167, 139, 250, 0.04) 100%);
  border: 1px solid rgba(124, 58, 237, 0.20);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 4px 18px rgba(124, 58, 237, 0.12);
}

/* Pastille statut générique (4 variantes) */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 500;
  background: rgba(124, 58, 237, 0.10);
  border: 1px solid rgba(124, 58, 237, 0.25);
  color: #c4b5fd;
}
.status-pill::before {
  content: '';
  width: 6px; height: 6px;
  background: currentColor;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-pill.success { background: rgba(16, 185, 129, 0.10); border-color: rgba(16, 185, 129, 0.30); color: #34d399; }
.status-pill.warning { background: rgba(234, 179, 8, 0.10);  border-color: rgba(234, 179, 8, 0.30);  color: #facc15; }
.status-pill.error   { background: rgba(239, 68, 68, 0.10);  border-color: rgba(239, 68, 68, 0.30);  color: #f87171; }

/* Titre de section avec barre verticale violet */
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 700;
  color: #ffffff;
  margin: 1.4rem 0 0.6rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(167, 139, 250, 0.10);
}
.section-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background: linear-gradient(180deg, #a78bfa 0%, #7c3aed 100%);
  border-radius: 2px;
  display: inline-block;
  flex-shrink: 0;
}

/* Séparateur subtil (gradient horizontal violet) */
.soft-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(167, 139, 250, 0.18) 50%, transparent 100%);
  margin: 1.5rem 0;
  border: none;
}
"""

# --- Formulaire générateur (glassmorphism, inputs, selects, checkboxes, bouton) ---
_CSS_GENERATOR_FORM = """
/* === FORMULAIRES (st.form) — CARTE GLASSMORPHISM === */
[data-testid="stForm"] {
  background: rgba(22, 26, 38, 0.55) !important;
  backdrop-filter: blur(14px) !important;
  -webkit-backdrop-filter: blur(14px) !important;
  border: 1px solid rgba(255, 255, 255, 0.06) !important;
  border-radius: 16px !important;
  padding: 26px 28px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.22), 0 0 0 1px rgba(124, 58, 237, 0.04) inset !important;
  margin-bottom: 1.25rem;
}

/* === LABELS DES CHAMPS === */
[data-testid="stForm"] label,
[data-testid="stForm"] [data-baseweb="form-control-label"] {
  color: rgba(255, 255, 255, 0.78) !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.2px;
  margin-bottom: 6px !important;
}

/* === ZONE TEXTE (sujet) === */
[data-testid="stForm"] textarea,
[data-testid="stForm"] [data-baseweb="textarea"] textarea {
  background: rgba(10, 13, 20, 0.55) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 12px !important;
  color: #ffffff !important;
  font-size: 0.95rem !important;
  line-height: 1.5 !important;
  padding: 12px 14px !important;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
}
[data-testid="stForm"] textarea:hover {
  border-color: rgba(167, 139, 250, 0.30) !important;
}
[data-testid="stForm"] textarea:focus,
[data-testid="stForm"] [data-baseweb="textarea"]:focus-within textarea {
  border-color: rgba(167, 139, 250, 0.55) !important;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.18) !important;
  background: rgba(10, 13, 20, 0.75) !important;
  outline: none !important;
}
[data-testid="stForm"] textarea::placeholder {
  color: rgba(255, 255, 255, 0.30) !important;
  font-style: normal !important;
}

/* === SELECTBOX (Secteur, Ton, Objectif, Type de contenu) === */
[data-testid="stForm"] [data-baseweb="select"] > div {
  background: rgba(10, 13, 20, 0.55) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 10px !important;
  min-height: 42px !important;
  transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
[data-testid="stForm"] [data-baseweb="select"] > div:hover {
  border-color: rgba(167, 139, 250, 0.30) !important;
}
[data-testid="stForm"] [data-baseweb="select"][aria-expanded="true"] > div,
[data-testid="stForm"] [data-baseweb="select"]:focus-within > div {
  border-color: rgba(167, 139, 250, 0.55) !important;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.18) !important;
}
[data-testid="stForm"] [data-baseweb="select"] [data-baseweb="select-control"] {
  color: #ffffff !important;
}
/* Liste déroulante du select */
[data-baseweb="popover"] [role="listbox"] {
  background: rgba(22, 26, 38, 0.96) !important;
  border: 1px solid rgba(167, 139, 250, 0.18) !important;
  border-radius: 10px !important;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
[data-baseweb="popover"] [role="option"] {
  color: rgba(255, 255, 255, 0.85) !important;
  font-size: 0.9rem !important;
  padding: 8px 12px !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"] {
  background: rgba(124, 58, 237, 0.14) !important;
  color: #ffffff !important;
}

/* === CHECKBOXES (plateformes) === */
[data-testid="stForm"] [data-testid="stCheckbox"] {
  padding: 4px 6px !important;
  border-radius: 8px;
  transition: background 0.15s ease;
}
[data-testid="stForm"] [data-testid="stCheckbox"]:hover {
  background: rgba(124, 58, 237, 0.06);
}
[data-testid="stForm"] [data-testid="stCheckbox"] label {
  color: rgba(255, 255, 255, 0.88) !important;
  font-size: 0.92rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
}
/* Style de la checkbox cochée — garde la couleur primaire mais avec un peu plus de pop */
[data-testid="stForm"] [data-testid="stCheckbox"] [data-baseweb="checkbox"] [role="checkbox"][aria-checked="true"] {
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%) !important;
  border-color: #7c3aed !important;
}

/* === BOUTON GÉNÉRER (bouton primaire submit) — plus impactant === */
[data-testid="stForm"] button[kind="primaryFormSubmit"],
[data-testid="stForm"] button[kind="primary"] {
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #6d28d9 100%) !important;
  background-size: 200% 200% !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  font-size: 1rem !important;
  letter-spacing: 0.3px !important;
  padding: 14px 24px !important;
  border-radius: 12px !important;
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.40), 0 0 0 1px rgba(167, 139, 250, 0.20) inset !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background-position 0.30s ease !important;
  margin-top: 0.6rem !important;
}
[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
[data-testid="stForm"] button[kind="primary"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 28px rgba(124, 58, 237, 0.55), 0 0 0 1px rgba(167, 139, 250, 0.30) inset !important;
  background-position: 100% 100% !important;
}
[data-testid="stForm"] button[kind="primaryFormSubmit"]:active,
[data-testid="stForm"] button[kind="primary"]:active {
  transform: translateY(0) !important;
}

/* === TITRE "Plateformes (coche celles que tu veux)" — markdown dans le form === */
[data-testid="stForm"] [data-testid="stMarkdownContainer"] strong {
  color: rgba(255, 255, 255, 0.92) !important;
}
"""

# ===========================================================================
# Modernisation 4 — Cartes plateformes brandées dans les onglets de résultats
# ===========================================================================
_CSS_PLATFORM_CARDS = """
.sc-platform-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  margin: 0.4rem 0 1rem 0;
  border-radius: 12px;
  background: rgba(22, 26, 38, 0.55);
  border-left: 4px solid var(--sc-primary);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  font-weight: 600;
  font-size: 0.98rem;
  color: rgba(255, 255, 255, 0.92);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
}
.sc-platform-banner .sc-pb-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 1.05rem;
  flex-shrink: 0;
}
.sc-platform-banner .sc-pb-name { flex: 1; letter-spacing: 0.2px; }
.sc-platform-banner .sc-pb-tag {
  font-size: 0.70rem;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: rgba(255, 255, 255, 0.55);
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
}

.sc-platform-linkedin       { border-left-color: #0A66C2; }
.sc-platform-linkedin .sc-pb-icon       { background: rgba(10, 102, 194, 0.18); color: #4d9ce6; }

.sc-platform-instagram      { border-left-color: #E1306C; background-image: linear-gradient(90deg, rgba(225,48,108,0.10) 0%, rgba(22,26,38,0.55) 60%); }
.sc-platform-instagram .sc-pb-icon      { background: linear-gradient(135deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; }

.sc-platform-facebook       { border-left-color: #1877F2; }
.sc-platform-facebook .sc-pb-icon       { background: rgba(24, 119, 242, 0.18); color: #4ea1ff; }

.sc-platform-tiktok         { border-left-color: #00f2ea; background-image: linear-gradient(90deg, rgba(255,0,80,0.08) 0%, rgba(0,242,234,0.06) 50%, rgba(22,26,38,0.55) 100%); }
.sc-platform-tiktok .sc-pb-icon         { background: linear-gradient(135deg, #ff0050 0%, #00f2ea 100%); color: white; }

.sc-platform-youtube_shorts { border-left-color: #FF0000; }
.sc-platform-youtube_shorts .sc-pb-icon { background: rgba(255, 0, 0, 0.18); color: #ff5e5e; }

.sc-platform-x_twitter      { border-left-color: #ffffff; }
.sc-platform-x_twitter .sc-pb-icon      { background: #000000; color: white; border: 1px solid rgba(255,255,255,0.20); }

.sc-platform-pinterest      { border-left-color: #E60023; }
.sc-platform-pinterest .sc-pb-icon      { background: rgba(230, 0, 35, 0.18); color: #ff5a6e; }

.sc-platform-threads        { border-left-color: #ffffff; }
.sc-platform-threads .sc-pb-icon        { background: #1a1a1a; color: white; border: 1px solid rgba(255,255,255,0.20); }

.sc-platform-snapchat       { border-left-color: #FFFC00; }
.sc-platform-snapchat .sc-pb-icon       { background: rgba(255, 252, 0, 0.18); color: #fffc70; }

.sc-platform-google_business { border-left-color: #4285F4; }
.sc-platform-google_business .sc-pb-icon { background: rgba(66, 133, 244, 0.18); color: #6da6ff; }

.sc-platform-blog_seo       { border-left-color: #7c3aed; }
.sc-platform-blog_seo .sc-pb-icon       { background: rgba(124, 58, 237, 0.18); color: #a78bfa; }

.sc-platform-email          { border-left-color: #94a3b8; }
.sc-platform-email .sc-pb-icon          { background: rgba(148, 163, 184, 0.18); color: #cbd5e1; }
"""

# ===========================================================================
# Modernisation 5 — Animation typewriter / fade-up sur les contenus générés
# ===========================================================================
_CSS_TYPEWRITER = """
@keyframes scFadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes scBlink {
  0%, 49%   { opacity: 1; }
  50%, 100% { opacity: 0; }
}
@keyframes scPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(167, 139, 250, 0.35); }
  50%      { box-shadow: 0 0 0 6px rgba(167, 139, 250, 0); }
}
[data-baseweb="tab-panel"] {
  animation: scFadeUp 0.42s ease both;
}
.sc-typewriter-line {
  display: flex;
  align-items: center;
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 0.6px;
  margin: 0.2rem 0 0.4rem 0;
  text-transform: uppercase;
  font-weight: 600;
}
.sc-typewriter-line .sc-tw-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #4ade80;
  margin-right: 8px;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.65);
  animation: scPulse 2s ease-in-out infinite;
}
.sc-typewriter-line .sc-tw-cursor {
  display: inline-block;
  width: 2px;
  height: 12px;
  background: var(--sc-accent);
  margin-left: 6px;
  animation: scBlink 1s steps(2) infinite;
  border-radius: 1px;
  vertical-align: middle;
}
"""

# ===========================================================================
# Modernisation 6 — Stats footer (X plateformes · Y mots · Z hashtags · ~30s)
# ===========================================================================
_CSS_STATS_FOOTER = """
.sc-stats-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 22px;
  margin: 1.4rem 0 0.6rem 0;
  padding: 14px 22px;
  background: rgba(22, 26, 38, 0.50);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.sc-stats-footer .sc-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.92rem;
  font-weight: 500;
}
.sc-stats-footer .sc-stat .sc-stat-num {
  font-size: 1.10rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.sc-stats-footer .sc-stat .sc-stat-lbl {
  color: rgba(255, 255, 255, 0.65);
  font-weight: 500;
}
.sc-stats-footer .sc-stat-sep {
  color: rgba(255, 255, 255, 0.22);
  font-weight: 300;
  font-size: 1.1rem;
}
"""

# ===========================================================================
# Modernisation 7 — Score d'engagement IA mocké + quick-regen buttons
# ===========================================================================
_CSS_SCORE_GAUGE = """
.sc-score-block {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 22px 26px;
  margin: 1.2rem 0 0.4rem 0;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.10) 0%, rgba(22, 26, 38, 0.55) 60%);
  border: 1px solid rgba(167, 139, 250, 0.16);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.sc-score-gauge {
  position: relative;
  width: 96px;
  height: 96px;
  flex-shrink: 0;
}
.sc-score-gauge svg { transform: rotate(-90deg); display: block; }
.sc-score-gauge .sc-score-track {
  fill: none;
  stroke: rgba(255, 255, 255, 0.07);
  stroke-width: 8;
}
.sc-score-gauge .sc-score-bar {
  fill: none;
  stroke: url(#sc-score-grad);
  stroke-width: 8;
  stroke-linecap: round;
}
.sc-score-gauge .sc-score-num {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.45rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.5px;
}
.sc-score-gauge .sc-score-num small {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.55);
  font-weight: 500;
  margin-left: 1px;
}
.sc-score-info { flex: 1; }
.sc-score-info h4 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.2px;
}
.sc-score-info p {
  margin: 0;
  font-size: 0.86rem;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.45;
}
.sc-score-badge {
  display: inline-block;
  margin-top: 8px;
  padding: 3px 10px;
  font-size: 0.70rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  border-radius: 6px;
  background: rgba(34, 197, 94, 0.18);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.28);
}
.sc-score-badge.warn { background: rgba(234, 179, 8, 0.16); color: #facc15; border-color: rgba(234, 179, 8, 0.28); }
.sc-score-badge.bad  { background: rgba(239, 68, 68, 0.16); color: #f87171; border-color: rgba(239, 68, 68, 0.28); }

.sc-quick-regen-title {
  margin: 1.0rem 0 0.4rem 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.62);
}
"""

# ===========================================================================
# Modernisation 8 — Cartes premium pour chaque résultat de plateforme
#                   + Aperçu visuel mobile mocké (effet "wow" démo)
# ===========================================================================
_CSS_RESULT_CARDS = """
@keyframes scSlideUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
.sc-result-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px 24px 20px 24px;
  margin: 0.6rem 0 1rem 0;
  background: linear-gradient(135deg, rgba(22, 26, 38, 0.72) 0%, rgba(15, 18, 28, 0.85) 100%);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 18px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.32), inset 0 0 0 1px rgba(167, 139, 250, 0.04);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  animation: scSlideUp 0.5s ease both;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
.sc-result-card:hover {
  transform: translateY(-2px);
  border-color: rgba(167, 139, 250, 0.22);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.40), inset 0 0 0 1px rgba(167, 139, 250, 0.10);
}
.sc-result-card.sc-platform-linkedin       { border-left: 3px solid #0A66C2; }
.sc-result-card.sc-platform-instagram      { border-left: 3px solid #E1306C; }
.sc-result-card.sc-platform-facebook       { border-left: 3px solid #1877F2; }
.sc-result-card.sc-platform-tiktok         { border-left: 3px solid #00f2ea; }
.sc-result-card.sc-platform-youtube_shorts { border-left: 3px solid #FF0000; }
.sc-result-card.sc-platform-x_twitter      { border-left: 3px solid #ffffff; }
.sc-result-card.sc-platform-pinterest      { border-left: 3px solid #E60023; }
.sc-result-card.sc-platform-threads        { border-left: 3px solid #ffffff; }
.sc-result-card.sc-platform-snapchat       { border-left: 3px solid #FFFC00; }
.sc-result-card.sc-platform-google_business { border-left: 3px solid #4285F4; }
.sc-result-card.sc-platform-blog_seo       { border-left: 3px solid #7c3aed; }
.sc-result-card.sc-platform-email          { border-left: 3px solid #94a3b8; }

.sc-rc-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.sc-rc-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 1.15rem;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}
.sc-rc-meta { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.sc-rc-meta h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.2px;
}
.sc-rc-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.62);
  font-weight: 500;
}
.sc-rc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.7);
  animation: scPulse 2s ease-in-out infinite;
  flex-shrink: 0;
}
.sc-rc-tag {
  margin-left: 4px;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  background: rgba(124, 58, 237, 0.16);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.22);
}

.sc-rc-text {
  font-size: 0.95rem;
  line-height: 1.62;
  color: rgba(255, 255, 255, 0.92);
  white-space: pre-wrap;
  word-wrap: break-word;
  user-select: text;
  padding: 4px 2px;
}

.sc-rc-cta {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.14) 0%, rgba(124, 58, 237, 0.04) 100%);
  border: 1px solid rgba(167, 139, 250, 0.18);
}
.sc-rc-cta-label {
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: #c4b5fd;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(124, 58, 237, 0.22);
  flex-shrink: 0;
}
.sc-rc-cta-text { font-size: 0.92rem; color: white; font-weight: 500; }

.sc-rc-hashtags { display: flex; flex-wrap: wrap; gap: 6px; }
.sc-hashtag-chip {
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 500;
  background: rgba(124, 58, 237, 0.10);
  color: #a78bfa;
  border: 1px solid rgba(167, 139, 250, 0.18);
  letter-spacing: 0.2px;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}
.sc-hashtag-chip:hover {
  background: rgba(124, 58, 237, 0.22);
  color: #c4b5fd;
  transform: translateY(-1px);
}

.sc-rc-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 6px;
}
.sc-rc-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 12px;
  border-radius: 12px;
  background: rgba(15, 18, 28, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}
.sc-rc-stat:hover {
  border-color: rgba(167, 139, 250, 0.22);
  background: rgba(22, 26, 38, 0.65);
  transform: translateY(-1px);
}
.sc-rc-stat .sc-rc-stat-num {
  font-size: 1.55rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.1;
}
.sc-rc-stat .sc-rc-stat-lbl {
  margin-top: 4px;
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.60);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

/* === Aperçu visuel mobile mocké === */
.sc-mock-phone {
  margin: 8px auto;
  max-width: 320px;
  background: linear-gradient(180deg, #0a0d14 0%, #131722 100%);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  padding: 14px 14px 16px 14px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.55), inset 0 0 0 1px rgba(255, 255, 255, 0.04);
  animation: scSlideUp 0.4s ease both;
}
.sc-mock-phone-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.sc-mock-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
  color: white;
  font-weight: 700;
  font-size: 0.92rem;
  flex-shrink: 0;
}
.sc-mock-username { font-size: 0.84rem; font-weight: 700; color: white; line-height: 1.2; }
.sc-mock-time { font-size: 0.68rem; color: rgba(255, 255, 255, 0.45); margin-top: 2px; }
.sc-mock-dots { margin-left: auto; color: rgba(255, 255, 255, 0.5); font-size: 1rem; letter-spacing: 1px; }
.sc-mock-image {
  margin: 10px 0;
  height: 120px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.30) 0%, rgba(167, 139, 250, 0.18) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: rgba(255, 255, 255, 0.65);
  border: 1px dashed rgba(167, 139, 250, 0.30);
}
.sc-mock-body {
  font-size: 0.82rem;
  line-height: 1.50;
  color: rgba(255, 255, 255, 0.88);
  margin-bottom: 8px;
  white-space: pre-wrap;
}
.sc-mock-hashtags { margin-top: 4px; font-size: 0.76rem; color: #6da6ff; font-weight: 500; word-break: break-word; }
.sc-mock-actions {
  display: flex;
  gap: 18px;
  padding-top: 10px;
  margin-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.65);
}
.sc-mock-actions span { transition: transform 0.15s ease, color 0.15s ease; }
.sc-mock-actions span:hover { transform: scale(1.15); color: white; }
"""

# --- Slot pour les futurs blocs CSS ---
# ===========================================================================
# Modernisation 9 — Polish final : images cards, publish n8n premium,
#                   responsive (desktop / tablet / mobile), cohérence visuelle
# ===========================================================================
_CSS_POLISH_FINAL = """
/* === COHÉRENCE GLOBALE — variables additionnelles === */
:root {
  --sc-radius-sm: 8px;
  --sc-radius-md: 12px;
  --sc-radius-lg: 16px;
  --sc-radius-xl: 18px;
  --sc-shadow-card: 0 8px 28px rgba(0, 0, 0, 0.28);
  --sc-shadow-hover: 0 14px 38px rgba(0, 0, 0, 0.40);
}

/* Séparateurs uniformes */
hr, [data-testid="stDividerLine"] {
  border-color: rgba(255, 255, 255, 0.08) !important;
  border-width: 1px 0 0 0 !important;
  margin: 1.4rem 0 !important;
}

/* Sous-titres de section uniformes */
.block-container h2,
.block-container h3,
.block-container [data-testid="stHeader"] {
  letter-spacing: -0.01em;
  color: rgba(255, 255, 255, 0.95);
}

/* Streamlit alerts polish (success / error / warning / info) */
[data-testid="stAlert"] {
  border-radius: var(--sc-radius-md) !important;
  border: 1px solid rgba(255, 255, 255, 0.07) !important;
  padding: 14px 18px !important;
  font-size: 0.92rem !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  margin-top: 0.5rem !important;
}
[data-testid="stAlert"][data-baseweb="notification"] { background: transparent !important; }

/* === IMAGES DALL-E — cartes cohérentes === */
.sc-img-card {
  background: linear-gradient(135deg, rgba(22, 26, 38, 0.72) 0%, rgba(15, 18, 28, 0.85) 100%);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: var(--sc-radius-lg);
  padding: 14px 14px 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
  animation: scSlideUp 0.5s ease both;
  height: 100%;
  box-sizing: border-box;
}
.sc-img-card:hover {
  transform: translateY(-3px);
  border-color: rgba(167, 139, 250, 0.25);
  box-shadow: var(--sc-shadow-hover);
}
.sc-img-card .sc-img-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.sc-img-card .sc-img-label {
  font-size: 0.86rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 0.2px;
}
.sc-img-card .sc-img-ratio {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(124, 58, 237, 0.18);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.25);
  white-space: nowrap;
}
/* Arrondis sur les images Streamlit dans les cartes images */
[data-testid="stImage"] img {
  border-radius: var(--sc-radius-md) !important;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.30);
}
.sc-img-download {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: var(--sc-radius-sm);
  background: rgba(124, 58, 237, 0.10);
  color: #a78bfa !important;
  border: 1px solid rgba(167, 139, 250, 0.22);
  text-decoration: none !important;
  font-size: 0.86rem;
  font-weight: 600;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
  text-align: center;
}
.sc-img-download:hover {
  background: rgba(124, 58, 237, 0.22);
  color: #c4b5fd !important;
  transform: translateY(-1px);
}

/* === PUBLISH N8N — carte premium === */
.sc-publish-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 22px 24px;
  margin: 0.6rem 0 1rem 0;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(22, 26, 38, 0.65) 60%);
  border: 1px solid rgba(167, 139, 250, 0.18);
  border-radius: var(--sc-radius-xl);
  box-shadow: var(--sc-shadow-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  animation: scSlideUp 0.4s ease both;
}
.sc-publish-header {
  display: flex;
  align-items: center;
  gap: 14px;
}
.sc-publish-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
  color: white;
  font-size: 1.20rem;
  flex-shrink: 0;
  box-shadow: 0 6px 16px rgba(124, 58, 237, 0.30);
}
.sc-publish-text { flex: 1; }
.sc-publish-text h4 {
  margin: 0 0 3px 0;
  font-size: 1.02rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.2px;
}
.sc-publish-text p {
  margin: 0;
  font-size: 0.86rem;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.50;
}
.sc-publish-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.74rem;
  font-weight: 600;
  letter-spacing: 0.4px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(74, 222, 128, 0.14);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.28);
}

/* === RESPONSIVE — desktop / tablet / mobile === */
/* Tablette (≤ 1024px) */
@media (max-width: 1024px) {
  .block-container { padding-top: 1.4rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
  .sc-result-card { padding: 18px 18px 16px 18px !important; }
  .sc-stats-footer { gap: 14px; padding: 12px 16px; }
  .sc-score-block { padding: 18px 20px; }
}

/* Tablette portrait & gros mobile (≤ 768px) */
@media (max-width: 768px) {
  .sc-stats-footer { flex-direction: column; gap: 10px; padding: 14px; }
  .sc-stats-footer .sc-stat-sep { display: none; }
  .sc-score-block { flex-direction: column; align-items: flex-start; gap: 14px; }
  .sc-result-card { padding: 16px !important; }
  .sc-rc-stats { grid-template-columns: repeat(3, 1fr); }
  .sc-rc-stat { padding: 10px 6px; }
  .sc-rc-stat .sc-rc-stat-num { font-size: 1.30rem; }
  .sc-mock-phone { max-width: 100%; }
  /* Tabs scrollables horizontalement */
  [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    flex-wrap: nowrap !important;
  }
}

/* Mobile (≤ 640px) */
@media (max-width: 640px) {
  .block-container { padding-left: 0.7rem !important; padding-right: 0.7rem !important; }
  [data-testid="stForm"] { padding: 18px 16px !important; }
  /* Le formulaire générateur passe en une colonne */
  [data-testid="stForm"] [data-testid="column"] { flex: 1 1 100% !important; min-width: 100% !important; }
  /* Cartes résultats en colonne unique */
  .sc-rc-text { font-size: 0.90rem; }
  .sc-rc-header { gap: 10px; padding-bottom: 10px; }
  .sc-rc-icon { width: 38px; height: 38px; }
  .sc-rc-stats { grid-template-columns: 1fr 1fr; gap: 8px; }
  .sc-rc-stat .sc-rc-stat-num { font-size: 1.40rem; }
  /* Stats footer : tout centré et empilé */
  .sc-stats-footer { padding: 12px 14px; }
  .sc-stats-footer .sc-stat { font-size: 0.86rem; }
  /* Score gauge plus compact */
  .sc-score-gauge { width: 80px; height: 80px; }
  .sc-score-gauge svg { width: 80px; height: 80px; }
  .sc-score-info h4 { font-size: 0.94rem; }
  .sc-score-info p { font-size: 0.80rem; }
  /* Boutons plus grands sur mobile */
  button[kind="primary"], button[kind="primaryFormSubmit"] {
    min-height: 48px !important;
    font-size: 0.98rem !important;
    padding: 12px 18px !important;
  }
  button[kind="secondary"] { min-height: 44px !important; }
  /* Plateforme banner plus compact */
  .sc-platform-banner { padding: 10px 14px; font-size: 0.92rem; }
  .sc-platform-banner .sc-pb-tag { display: none; }
  /* Publish card plus compact */
  .sc-publish-card { padding: 16px 18px; }
  .sc-publish-icon { width: 40px; height: 40px; font-size: 1.1rem; }
  .sc-publish-text h4 { font-size: 0.96rem; }
  .sc-publish-text p { font-size: 0.82rem; }
  /* Aperçu mobile mock prend toute la largeur */
  .sc-mock-phone { max-width: 100%; padding: 12px; }
  /* Sidebar : déjà gérée par Streamlit (collapse), on évite tout débordement */
  section[data-testid="stSidebar"] { width: 280px !important; }
}
"""
_CSS_FUTURE = """
/* Réservé pour les futures additions UI */
"""

# Concaténation finale — rendu identique au monolithique précédent.
GLOBAL_CSS = (
    "<style>"
    + _CSS_VARS
    + _CSS_LAYOUT
    + _CSS_TYPOGRAPHY
    + _CSS_BUTTONS
    + _CSS_INPUTS_TABS
    + _CSS_METRICS
    + _CSS_ALERTS_CODE
    + _CSS_FOOTER_HERO
    + _CSS_SIDEBAR
    + _CSS_LAYOUT_PREMIUM
    + _CSS_GENERATOR_FORM
    + _CSS_PLATFORM_CARDS
    + _CSS_TYPEWRITER
    + _CSS_STATS_FOOTER
    + _CSS_SCORE_GAUGE
    + _CSS_POLISH_FINAL
    + _CSS_RESULT_CARDS
    + _CSS_FUTURE
    + "</style>"
)


def inject_brand() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    # Pastille statut backend en haut à droite (zone principale, fixed glassmorphism)
    try:
        ok, _info = api_health()
    except Exception:
        ok = False
    if ok:
        st.markdown(
            '<div class="sc-status-pill-top">Backend en ligne</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sc-status-pill-top offline">Backend hors ligne</div>',
            unsafe_allow_html=True,
        )


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

# (slug → (libellé court, icône emoji)) — utilisé pour les cartes brandées
PLATFORM_META: dict[str, tuple[str, str]] = {
    "linkedin": ("LinkedIn", "in"),
    "instagram": ("Instagram", "📷"),
    "facebook": ("Facebook", "f"),
    "tiktok": ("TikTok", "♪"),
    "youtube_shorts": ("YouTube Shorts", "▶"),
    "x_twitter": ("X / Twitter", "𝕏"),
    "pinterest": ("Pinterest", "P"),
    "threads": ("Threads", "@"),
    "snapchat": ("Snapchat", "👻"),
    "google_business": ("Google Business", "G"),
    "blog_seo": ("Blog SEO", "📰"),
    "email": ("Email", "✉"),
}


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
        # --- Logo ---
        st.markdown(LOGO_SVG, unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # --- Statut backend (pill premium) ---
        ok, info = api_health()
        if ok:
            st.markdown(
                '<div class="sc-status-online">Backend en ligne</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="sc-status-offline">Backend hors ligne</div>'
                f'<div style="font-size:0.7rem;color:rgba(248,113,113,0.7);margin-top:4px">{info}</div>',
                unsafe_allow_html=True,
            )

        # --- Carte utilisateur (si connecté) ---
        if _logged_in():
            plan_value = (st.session_state.user_plan or "free").upper()
            company_html = ""
            if st.session_state.user_company:
                company_html = (
                    '<div class="sc-user-row">'
                    '<span class="sc-user-icon">🏢</span>'
                    f'<span>{st.session_state.user_company}</span>'
                    '</div>'
                )
            user_card = (
                '<div class="sc-user-card">'
                '<div class="sc-user-row">'
                '<span class="sc-user-icon">👤</span>'
                f'<span>{st.session_state.user_email}</span>'
                '</div>'
                f'{company_html}'
                '<div class="sc-user-row">'
                '<span class="sc-user-icon">⚡</span>'
                '<span>Plan</span>'
                f'<span class="sc-plan-badge">{plan_value}</span>'
                '</div>'
                '</div>'
            )
            st.markdown(user_card, unsafe_allow_html=True)
            pages = ["Générateur", "Tableau de bord", "Historique", "n8n Status", "Paramètres"]
        else:
            pages = ["Connexion"]

        # Force page from regen action (set before the radio renders)
        forced = st.session_state.pop("force_page", None)
        if forced and forced in pages:
            st.session_state["nav_radio"] = forced

        # --- Navigation (label masqué, styling via CSS) ---
        choice = st.radio("Navigation", pages, key="nav_radio", label_visibility="collapsed")

        # --- Déconnexion ---
        if _logged_in():
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            if st.button("🚪 Déconnexion", use_container_width=True):
                for k in ["auth_token", "user_id", "user_email", "user_company", "user_plan", "last_generation"]:
                    st.session_state[k] = None
                st.rerun()

        # --- Infos en bas (API + n8n URLs) ---
        st.markdown(
            '<div class="sc-info-bottom">'
            f'<div class="sc-info-row"><span>API</span><code>{API_BASE}</code></div>'
            f'<div class="sc-info-row"><span>n8n</span><code>{N8N_WEBHOOK}</code></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    return choice


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
# ===========================================================================
# PAGE — Connexion / Inscription
# ===========================================================================
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


# ===========================================================================
# PAGE — Générateur (formulaire + résultats + images + n8n)
# ===========================================================================
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

                # === MODERNISATION 8 — Carte premium par plateforme ===
                meta_label, meta_icon = PLATFORM_META.get(
                    name, (name.replace("_", " ").title(), "✨")
                )
                texte = (data.get("texte") or "").strip()
                cta = (data.get("cta") or "").strip()
                hashtags_list = data.get("hashtags") or []
                nb_mots = int(data.get("longueur_mots", 0) or 0)

                safe_text = _html.escape(texte) if texte else ""
                safe_cta = _html.escape(cta) if cta else ""

                # Hashtags chips (fallback : bloc vide masqué si absent)
                if hashtags_list:
                    chips_html = "".join(
                        f'<span class="sc-hashtag-chip">#{_html.escape(str(h).lstrip("#"))}</span>'
                        for h in hashtags_list
                    )
                    hashtags_block_html = f'<div class="sc-rc-hashtags">{chips_html}</div>'
                else:
                    hashtags_block_html = ""

                # Bloc CTA (fallback masqué si absent)
                cta_block_html = (
                    f'<div class="sc-rc-cta">'
                    f'<span class="sc-rc-cta-label">CTA</span>'
                    f'<span class="sc-rc-cta-text">{safe_cta}</span>'
                    f'</div>'
                ) if safe_cta else ""

                # Texte (fallback propre si vide)
                text_html = (
                    safe_text
                    if safe_text
                    else '<em style="color:rgba(255,255,255,0.45)">Aucun texte généré pour cette plateforme.</em>'
                )

                cta_stat = "✓" if cta else "—"

                card_html = (
                    f'<div class="sc-result-card sc-platform-{name}">'
                    f'<div class="sc-rc-header">'
                    f'<div class="sc-rc-icon">{meta_icon}</div>'
                    f'<div class="sc-rc-meta">'
                    f'<h3>{_html.escape(meta_label)}</h3>'
                    f'<div class="sc-rc-status">'
                    f'<span class="sc-rc-dot"></span>'
                    f'<span>À l\'instant</span>'
                    f'<span class="sc-rc-tag">IA</span>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                    f'<div class="sc-rc-text">{text_html}</div>'
                    f'{cta_block_html}'
                    f'{hashtags_block_html}'
                    f'<div class="sc-rc-stats">'
                    f'<div class="sc-rc-stat"><div class="sc-rc-stat-num">{nb_mots}</div><div class="sc-rc-stat-lbl">Mots</div></div>'
                    f'<div class="sc-rc-stat"><div class="sc-rc-stat-num">{len(hashtags_list)}</div><div class="sc-rc-stat-lbl">Hashtags</div></div>'
                    f'<div class="sc-rc-stat"><div class="sc-rc-stat-num">{cta_stat}</div><div class="sc-rc-stat-lbl">CTA</div></div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                # === Aperçu visuel mobile mocké (effet "wow" démo) ===
                with st.expander("👁️ Aperçu visuel"):
                    mock_text = texte[:280] + ("…" if len(texte) > 280 else "")
                    mock_hashtags = " ".join(
                        f"#{str(h).lstrip('#')}" for h in (hashtags_list[:5] if hashtags_list else [])
                    )
                    avatar_letter = (meta_label[:1] if meta_label else "✨").upper()
                    mock_text_html = (
                        _html.escape(mock_text)
                        if mock_text
                        else '<em style="color:rgba(255,255,255,0.4)">Aucun texte à prévisualiser.</em>'
                    )
                    mock_html = (
                        f'<div class="sc-mock-phone">'
                        f'<div class="sc-mock-phone-header">'
                        f'<div class="sc-mock-avatar">{avatar_letter}</div>'
                        f'<div>'
                        f'<div class="sc-mock-username">votre_marque</div>'
                        f'<div class="sc-mock-time">il y a 5 secondes · {_html.escape(meta_label)}</div>'
                        f'</div>'
                        f'<div class="sc-mock-dots">⋯</div>'
                        f'</div>'
                        f'<div class="sc-mock-image">{meta_icon}</div>'
                        f'<div class="sc-mock-body">{mock_text_html}</div>'
                        f'<div class="sc-mock-hashtags">{_html.escape(mock_hashtags)}</div>'
                        f'<div class="sc-mock-actions">'
                        f'<span>♡</span><span>💬</span><span>↗</span>'
                        f'<span style="margin-left:auto;color:rgba(255,255,255,0.4)">···</span>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(mock_html, unsafe_allow_html=True)

                # === Texte brut accessible (pour copier rapidement) ===
                with st.expander("📋 Voir le texte brut (pour copier)"):
                    st.code(texte if texte else "(vide)", language="text")

    # ===== Stats footer global (Modernisation 6) =====
    if plat_results:
        total_plats = len(plat_results)
        total_mots = sum(int(d.get("longueur_mots", 0) or 0) for d in plat_results.values())
        total_hashtags = sum(len(d.get("hashtags", []) or []) for d in plat_results.values())
        # Estimation de durée ~ 4 secondes par plateforme (générée séquentiellement)
        duree_est = max(15, total_plats * 4)
        st.markdown(
            '<div class="sc-stats-footer">'
            f'<div class="sc-stat"><span class="sc-stat-num">{total_plats}</span><span class="sc-stat-lbl">plateformes</span></div>'
            '<span class="sc-stat-sep">·</span>'
            f'<div class="sc-stat"><span class="sc-stat-num">{total_mots}</span><span class="sc-stat-lbl">mots</span></div>'
            '<span class="sc-stat-sep">·</span>'
            f'<div class="sc-stat"><span class="sc-stat-num">{total_hashtags}</span><span class="sc-stat-lbl">hashtags</span></div>'
            '<span class="sc-stat-sep">·</span>'
            f'<div class="sc-stat"><span class="sc-stat-num">~{duree_est}s</span><span class="sc-stat-lbl">généré</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ===== Score d'engagement IA mocké + quick-regen (Modernisation 7) =====
    if plat_results:
        # Heuristique de score (mockée mais cohérente) :
        #   base 70 + bonus si CTA présents + bonus si hashtags ≥ 5/plateforme + bonus diversité
        plats_with_cta = sum(1 for d in plat_results.values() if d.get("cta"))
        avg_hashtags = (sum(len(d.get("hashtags", []) or []) for d in plat_results.values())
                        / max(1, len(plat_results)))
        score = 70
        score += int(min(15, plats_with_cta * 1.5))
        score += int(min(10, avg_hashtags))
        score = min(98, max(55, score))
        # Couleur badge selon score
        if score >= 80:
            badge_cls, badge_lbl = "", "Excellent"
        elif score >= 70:
            badge_cls, badge_lbl = "warn", "Correct"
        else:
            badge_cls, badge_lbl = "bad", "À améliorer"

        # Stroke-dashoffset pour le cercle (rayon 40 → circumference ≈ 251.33)
        circumference = 251.33
        offset = circumference * (1 - score / 100)
        st.markdown(
            '<div class="sc-score-block">'
            '<div class="sc-score-gauge">'
            '<svg width="96" height="96" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">'
            '<defs>'
            '<linearGradient id="sc-score-grad" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0%" stop-color="#a78bfa"/>'
            '<stop offset="100%" stop-color="#7c3aed"/>'
            '</linearGradient>'
            '</defs>'
            '<circle class="sc-score-track" cx="48" cy="48" r="40"></circle>'
            f'<circle class="sc-score-bar" cx="48" cy="48" r="40" '
            f'stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"></circle>'
            '</svg>'
            f'<div class="sc-score-num">{score}<small>/100</small></div>'
            '</div>'
            '<div class="sc-score-info">'
            '<h4>Score d\'engagement prédit</h4>'
            '<p>Estimation IA basée sur la présence de CTA, le nombre de hashtags et la diversité des plateformes générées.</p>'
            f'<span class="sc-score-badge {badge_cls}">{badge_lbl}</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Quick-regen buttons (3 prompts rapides)
        st.markdown('<div class="sc-quick-regen-title">⚡ Régénération rapide</div>', unsafe_allow_html=True)
        qr_cols = st.columns(3)
        last_sujet = (gen.get("sujet") or "").strip()
        last_secteur = (gen.get("content", {}) or {}).get("secteur") or ""
        last_ton = (gen.get("content", {}) or {}).get("ton") or ""
        last_plats = list(plat_results.keys())
        quick_modifiers = [
            ("😂 Plus humoristique", "Rends ce contenu plus humoristique et léger"),
            ("🚀 Plus viral", "Optimise ce contenu pour qu'il devienne viral (hook ultra fort)"),
            ("✂️ Plus court", "Raccourcis ce contenu de 30% en gardant l'essentiel"),
        ]
        for col, (label, modifier) in zip(qr_cols, quick_modifiers):
            if col.button(label, key=f"qr_{label}", use_container_width=True):
                st.session_state.regen_data = {
                    "sujet": f"{last_sujet}\n\n[Instruction additionnelle : {modifier}]",
                    "secteur": last_secteur,
                    "ton": last_ton,
                    "plateformes": last_plats,
                }
                st.session_state.force_page = "Générateur"
                st.toast(f"Mode régénération activé : {label}", icon="✨")
                st.rerun()

    if global_tags:
        st.write("---")
        st.write("**🌐 12 hashtags globaux :** " + " ".join(global_tags))

    # === MODERNISATION 9 — Images DALL-E (cartes premium responsives) ===
    images = content.get("images") or {}
    images_real = {k: v for k, v in images.items() if k != "errors" and isinstance(v, str)}
    if images_real:
        st.divider()
        st.subheader("🎨 Images générées par DALL-E 3")
        st.caption("Images générées par IA · URLs valides 60 minutes — télécharge-les si tu veux les conserver.")
        cols = st.columns(3)
        layout_map = [
            ("square",    "Instagram / Facebook",     "1:1"),
            ("landscape", "LinkedIn / Blog SEO",      "16:9"),
            ("portrait",  "TikTok / Reels / Stories", "9:16"),
        ]
        for col, (key, label, ratio) in zip(cols, layout_map):
            url = images_real.get(key)
            with col:
                # Ouverture de la carte image (HTML)
                st.markdown('<div class="sc-img-card">', unsafe_allow_html=True)
                if url:
                    st.image(url, use_container_width=True)
                    st.markdown(
                        f'<div class="sc-img-meta">'
                        f'<span class="sc-img-label">{label}</span>'
                        f'<span class="sc-img-ratio">{ratio}</span>'
                        f'</div>'
                        f'<a href="{url}" target="_blank" class="sc-img-download">'
                        f'📥 Télécharger l\'image'
                        f'</a>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="sc-img-meta">'
                        f'<span class="sc-img-label">{label}</span>'
                        f'<span class="sc-img-ratio">{ratio}</span>'
                        f'</div>'
                        f'<div style="padding:24px 12px;text-align:center;color:rgba(255,255,255,0.45);'
                        f'background:rgba(15,18,28,0.55);border-radius:12px;border:1px dashed rgba(255,255,255,0.10);">'
                        f'Format non disponible'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown('</div>', unsafe_allow_html=True)
    elif images.get("errors"):
        st.warning(f"⚠️ Génération images partiellement échouée : {images.get('errors')}")

    # === MODERNISATION 9 — Publication via n8n (carte premium) ===
    st.divider()
    st.markdown(
        '<div class="sc-publish-card">'
        '<div class="sc-publish-header">'
        '<div class="sc-publish-icon">📤</div>'
        '<div class="sc-publish-text">'
        '<h4>Publier via n8n</h4>'
        '<p>Envoie le contenu généré au workflow n8n (12 publishers en parallèle). '
        'Le statut passera automatiquement à <em>publié</em> dans l\'historique.</p>'
        '</div>'
        '<span class="sc-publish-status-pill">● Prêt</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if st.button("🚀 Envoyer au workflow n8n", type="primary", use_container_width=True):
        with st.spinner("Envoi du webhook…"):
            try:
                r = api_publish({
                    "content_id": gen.get("id"),
                    "user_id": st.session_state.user_id,
                    "plateformes": list(plat_results.keys()),
                    "payload": content,
                })
                if r.ok:
                    st.success(f"✅ Webhook OK — {r.json()}")
                else:
                    st.error(f"❌ Échec ({r.status_code}) — {r.text}")
            except Exception as exc:
                st.error(f"❌ Erreur réseau : {exc}")


# ===========================================================================
# PAGE — Tableau de bord (métriques + roadmap)
# ===========================================================================
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


# ===========================================================================
# PAGE — Historique
# ===========================================================================
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


# ===========================================================================
# PAGE — n8n Status
# ===========================================================================
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


# ===========================================================================
# PAGE — Paramètres
# ===========================================================================
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


# ===========================================================================
# Entry
# ===========================================================================
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
