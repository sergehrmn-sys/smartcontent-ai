<div align="center">

# 🪄 SmartContent AI

**Génération et publication automatique de contenu marketing IA multi-plateformes**

Une idée → 12 posts adaptés (LinkedIn, Instagram, Facebook, TikTok, YouTube Shorts, X, Pinterest, Threads, Snapchat, Google Business, Blog SEO, Email) + 3 images DALL-E → publication via n8n, en moins de 2 minutes.

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.57-FF4B4B?logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20%2B%20DALL--E%203-412991?logo=openai&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Workflow-EA4B71?logo=n8n&logoColor=white)

**Projet de fin d'études — AEC Intelligence Artificielle Appliquée — Collège Multihexa (Montréal, 2026)**

</div>

---

## 🎯 Le problème

Les PME québécoises (restaurants, salons, garages, immobilier, etc.) ont besoin d'être présentes sur les réseaux sociaux mais :

- **Manque de temps** pour rédiger 12 posts adaptés à chaque plateforme
- **Manque de compétences** en copywriting et design
- **Coût élevé** des agences marketing (1 500 – 4 000 $ CAD / mois)

## ✨ La solution

**SmartContent AI** automatise toute la chaîne : génération → adaptation par plateforme → visuels → publication.

| Étape | Outil | Durée |
|---|---|---|
| Texte 12 plateformes (ton, secteur, objectif personnalisés) | OpenAI GPT-4o | ~30-60 sec |
| 12 hashtags globaux pertinents | OpenAI GPT-4o | ~3 sec |
| 3 images IA (square, landscape, portrait) | DALL-E 3 | ~15-20 sec |
| Orchestration multi-plateformes | n8n workflow (12 publishers parallèles) | ~120 ms |
| Persistance | Supabase (PostgreSQL + JSONB) | — |

**Total : 1-2 minutes pour une campagne complète.**

## 🏗 Architecture

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Streamlit UI    │ ───▶ │  FastAPI         │ ───▶ │  OpenAI API      │
│  (port 8501)     │      │  (port 8001)     │      │  GPT-4o + DALL-E │
└──────────────────┘      └────────┬─────────┘      └──────────────────┘
                                   │
                                   ├──▶ Supabase (PostgreSQL)
                                   │     • users
                                   │     • contents (JSONB)
                                   │
                                   └──▶ n8n webhook (port 5678)
                                         └─▶ Switch → 12 publishers
                                             → Aggregator → Response
```

## 📸 Aperçu

| Page | Description |
|---|---|
| **Connexion / Inscription** | Auth bcrypt + JWT |
| **Générateur** | Formulaire → 12 onglets résultats + 3 images + bouton n8n |
| **Tableau de bord** | Métriques live + graphique répartition par plateforme + roadmap |
| **Historique** | Filtres (statut/plateforme), recherche, modifier & régénérer, supprimer, export CSV |
| **n8n Status** | URL webhook + ping de test + guide de configuration |
| **Paramètres** | Infos compte + URLs API |

## 🧩 Stack technique

**Backend** — FastAPI · Pydantic v2 · python-jose (JWT) · bcrypt · supabase-py · OpenAI SDK
**Frontend** — Streamlit 1.57 (theme custom violet `#7c3aed`)
**Base de données** — Supabase (PostgreSQL 15 + JSONB)
**IA** — OpenAI GPT-4o (textes + hashtags) + DALL-E 3 (images, 3 formats parallèles)
**Automatisation** — n8n Desktop (workflow 17 nodes, 12 publishers en parallèle)
**Déploiement** — Local / Docker-ready (prod sur Render + Vercel + Supabase Cloud envisagé)

## ⚙️ Setup local

### Prérequis

- Python 3.14
- Compte Supabase ([supabase.com](https://supabase.com))
- Clé API OpenAI ([platform.openai.com](https://platform.openai.com))
- n8n Desktop ([n8n.io/desktop](https://n8n.io/desktop))

### Installation

```powershell
git clone https://github.com/<TON-USERNAME>/smartcontent-ai-v2.git
cd smartcontent-ai-v2
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration

1. Copie `.env.example` → `.env` et remplis tes clés (OpenAI, Supabase URL + service-role key, etc.)
2. Dans Supabase Studio → SQL Editor → exécute `docs/supabase_schema.sql`

### Lancement

```powershell
# Fenêtre 1 — Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Fenêtre 2 — Frontend
streamlit run frontend/app.py --server.port 8501
```

Ouvre **http://localhost:8501** → inscription → générateur → c'est parti.

## 📂 Structure du projet

```
smartcontent-ai-v2/
├── backend/
│   ├── main.py                 # FastAPI app + CORS + routers
│   ├── config.py               # pydantic-settings (.env)
│   ├── models/schemas.py       # Pydantic request/response models
│   ├── routes/
│   │   ├── auth.py             # /auth/register + /auth/login
│   │   ├── generate.py         # /generate/ + /generate/publish
│   │   └── history.py          # /history/{user_id} + DELETE
│   └── services/
│       ├── openai_service.py   # GPT-4o multi-plateformes + DALL-E 3
│       └── supabase_service.py # Client service-role
├── frontend/
│   └── app.py                  # Streamlit 6 pages, theme violet
├── n8n/
│   └── smartcontent_workflow.json   # Workflow 17 nodes (12 publishers)
├── docs/
│   └── supabase_schema.sql     # DDL complet (users + contents)
├── .env.example
├── .gitignore
├── requirements.txt
├── test_api.py                 # Smoke tests
└── README.md
```

## 🗺 Roadmap

**MVP — terminé ✅**
- Auth, génération multi-plateformes, images DALL-E, n8n workflow, historique avancé

**Phase 2 — post-soutenance**
- Publication automatique réelle (LinkedIn / Meta API approuvées)
- Programmation des posts (calendrier marketing IA)
- Génération vidéo IA (Runway / Veo + ElevenLabs voix off)
- Analyse des performances (likes, vues, clics)
- Gestion multi-entreprises (agences)
- Bibliothèque de modèles + suggestions IA

**Phase 3 — produit commercial**
- Refonte frontend Next.js + PWA mobile
- Stripe (plans Free / Starter 29 $ / Pro 79 $ / Agency 199 $)
- Conformité Loi 25 (Québec) + RGPD

## 📊 Coûts opérationnels (par campagne)

| Item | Coût |
|---|---|
| GPT-4o textes (12 plateformes) | ~0.05 $ CAD |
| GPT-4o hashtags globaux | ~0.005 $ CAD |
| DALL-E 3 (3 images standard) | ~0.16 $ CAD |
| **Total par campagne** | **~0.22 $ CAD** |

## 🎓 Contexte académique

Projet réalisé dans le cadre de l'**AEC Intelligence Artificielle Appliquée** au **Collège Multihexa** (Montréal, Québec).
Auteur : **Serge Tsebo**
Soutenance : **Mai 2026**

## 📄 Licence

Projet pédagogique — tous droits réservés. Utilisation commerciale soumise à autorisation.

---

<div align="center">
<sub>Built with ☕, GPT-4o et beaucoup de café</sub>
</div>
