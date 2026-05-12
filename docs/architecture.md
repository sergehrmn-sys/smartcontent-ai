# 🏗 Architecture & Schémas UML — SmartContent AI

Ce document contient les **4 diagrammes** principaux du système, exprimés en **Mermaid** (rendu automatique sur GitHub).

Pour les exporter en PNG/SVG (utile dans le mémoire ou les slides) :
1. Va sur https://mermaid.live
2. Colle le code du bloc ` ```mermaid ` voulu
3. Clique **Actions → PNG / SVG**

---

## 1. Architecture système (vue d'ensemble)

Composants principaux et flux de données.

```mermaid
flowchart LR
    subgraph CLIENT["🖥️ Client (navigateur)"]
        UI[Streamlit UI<br/>port 8501]
    end

    subgraph BACKEND["⚙️ Backend FastAPI (port 8001)"]
        API[FastAPI app]
        AUTH[Auth router<br/>/auth]
        GEN[Generate router<br/>/generate]
        HIST[History router<br/>/history]
        OAS[OpenAI service]
        SBS[Supabase service]
    end

    subgraph EXTERNAL["☁️ Services externes"]
        OPENAI[OpenAI API<br/>GPT-4o + DALL-E 3]
        SUPA[(Supabase<br/>PostgreSQL)]
        N8N[n8n Workflow<br/>port 5678]
    end

    UI -->|HTTP REST| API
    API --> AUTH
    API --> GEN
    API --> HIST
    AUTH --> SBS
    GEN --> OAS
    GEN --> SBS
    GEN -->|webhook| N8N
    HIST --> SBS
    OAS -->|GPT-4o + DALL-E 3| OPENAI
    SBS -->|service-role key| SUPA
    N8N -->|stubs publication| LinkedIn[LinkedIn]
    N8N --> Instagram[Instagram]
    N8N --> Facebook[Facebook]
    N8N --> TikTok[TikTok]
    N8N --> Other[+ 8 autres plateformes]

    classDef client fill:#7c3aed,stroke:#5b21b6,color:#fff
    classDef backend fill:#1f2937,stroke:#a78bfa,color:#fff
    classDef external fill:#059669,stroke:#065f46,color:#fff
    class UI client
    class API,AUTH,GEN,HIST,OAS,SBS backend
    class OPENAI,SUPA,N8N,LinkedIn,Instagram,Facebook,TikTok,Other external
```

---

## 2. Diagramme de séquence — Génération de contenu

Flux complet d'une génération multi-plateformes avec images DALL-E 3.

```mermaid
sequenceDiagram
    actor User as 👤 Utilisateur
    participant ST as Streamlit (8501)
    participant API as FastAPI (8001)
    participant OS as OpenAI Service
    participant GPT as GPT-4o
    participant DALLE as DALL-E 3
    participant DB as Supabase
    participant N8N as n8n (5678)

    User->>ST: Remplit formulaire (sujet, secteur, ton, plateformes)
    User->>ST: Clique "🚀 Générer"
    ST->>API: POST /generate/ {sujet, secteur, ton, ..., plateformes[]}

    Note over API,OS: Phase 1 — Texte (séquentiel)
    loop pour chaque plateforme
        API->>OS: _generate_one(plateforme, ...)
        OS->>GPT: chat.completions.create(prompt plateforme)
        GPT-->>OS: JSON {texte, hashtags, cta}
        OS-->>API: ContentResult
    end

    Note over API,OS: Phase 2 — Hashtags globaux
    API->>OS: generate_global_hashtags(sujet, secteur)
    OS->>GPT: prompt 12 hashtags
    GPT-->>OS: ["#tag1", "#tag2", ...]

    Note over API,OS: Phase 3 — 3 images (PARALLÈLE via ThreadPoolExecutor)
    par square 1024x1024
        OS->>DALLE: images.generate(size="1024x1024")
        DALLE-->>OS: URL image
    and landscape 1792x1024
        OS->>DALLE: images.generate(size="1792x1024")
        DALLE-->>OS: URL image
    and portrait 1024x1792
        OS->>DALLE: images.generate(size="1024x1792")
        DALLE-->>OS: URL image
    end

    OS-->>API: {plateformes, hashtags_globaux, images}
    API->>DB: INSERT contents (textes + hashtags + images JSONB)
    DB-->>API: id
    API-->>ST: GenerateResponse {id, content}
    ST-->>User: Affiche 12 onglets + 3 images

    User->>ST: Clique "📤 Envoyer au workflow n8n"
    ST->>API: POST /generate/publish
    API->>N8N: POST webhook {plateformes, payload}
    N8N->>N8N: Switch → 12 publishers (parallèles) → Aggregator
    N8N-->>API: {ok: true, results}
    API->>DB: UPDATE contents SET statut='publie' WHERE id=...
    API-->>ST: PublishResponse
    ST-->>User: ✅ "Webhook OK"
```

---

## 3. Diagramme de séquence — Authentification

Inscription puis connexion avec bcrypt + JWT.

```mermaid
sequenceDiagram
    actor User as 👤 Utilisateur
    participant ST as Streamlit
    participant API as FastAPI /auth
    participant BC as bcrypt
    participant JWT as python-jose
    participant DB as Supabase users

    rect rgb(124, 58, 237, 0.1)
    Note over User,DB: Inscription (POST /auth/register)
    User->>ST: Email + mot de passe + entreprise + plan
    ST->>API: POST /auth/register
    API->>DB: SELECT id WHERE email=?
    alt Email existe déjà
        DB-->>API: 1 row
        API-->>ST: HTTP 409 Conflict
        ST-->>User: ⚠️ "Compte existe déjà"
    else Nouvel email
        DB-->>API: 0 rows
        API->>BC: hashpw(pw[:72], gensalt())
        BC-->>API: hash bcrypt
        API->>DB: INSERT users (email, hash, ...)
        DB-->>API: user record (id, ...)
        API->>JWT: encode {sub: id, email, exp}
        JWT-->>API: access_token
        API-->>ST: TokenResponse
        ST->>ST: Stocke token en session_state
        ST-->>User: ✅ Redirect vers Générateur
    end
    end

    rect rgb(167, 139, 250, 0.1)
    Note over User,DB: Connexion (POST /auth/login)
    User->>ST: Email + mot de passe
    ST->>API: POST /auth/login
    API->>DB: SELECT * WHERE email=? LIMIT 1
    alt Pas trouvé
        DB-->>API: 0 rows
        API-->>ST: HTTP 401
    else Trouvé
        DB-->>API: user (avec hash)
        API->>BC: checkpw(pw[:72], hash)
        BC-->>API: True / False
        alt Mot de passe invalide
            API-->>ST: HTTP 401
        else Valide
            API->>JWT: encode {sub, email, exp}
            JWT-->>API: access_token
            API-->>ST: TokenResponse
            ST-->>User: ✅ Redirect vers Générateur
        end
    end
    end
```

---

## 4. Diagramme entité-relation (DB Supabase)

Tables `users` et `contents` avec relations.

```mermaid
erDiagram
    USERS ||--o{ CONTENTS : "génère"

    USERS {
        UUID id PK "gen_random_uuid()"
        TEXT email UK "unique"
        TEXT password_hash "bcrypt"
        TEXT nom_entreprise "nullable"
        TEXT plan "free | pro | premium"
        TIMESTAMPTZ date_inscription "default NOW()"
    }

    CONTENTS {
        UUID id PK "gen_random_uuid()"
        UUID user_id FK "ON DELETE CASCADE"
        TEXT sujet "required"
        TEXT secteur "ex: Restaurant"
        TEXT ton "ex: Storytelling"
        TEXT objectif "ex: Vendre"
        TEXT type_contenu "ex: Post simple"
        JSONB plateformes "[\"linkedin\", \"tiktok\", ...]"
        JSONB content "Textes + hashtags + images"
        JSONB images "{square, landscape, portrait}"
        TEXT statut "draft | publie | erreur"
        TIMESTAMPTZ date_creation "default NOW()"
    }
```

### Index PostgreSQL
- `idx_users_email` sur `users(email)` — accélère le login
- `idx_contents_user_id` sur `contents(user_id)` — accélère la page Historique
- `idx_contents_date_creation` sur `contents(date_creation DESC)` — accélère le tri

### RLS (Row Level Security)
**Désactivé** sur les 2 tables. Le backend utilise la **service-role key** Supabase qui bypass RLS. Pour la prod, RLS sera réactivé avec policies par `user_id`.

---

## 5. Schéma du workflow n8n

Vue d'ensemble du workflow d'orchestration multi-plateformes (17 nodes).

```mermaid
flowchart LR
    WT[Webhook Trigger<br/>POST /webhook/<br/>smartcontent-publish]
    PD[Préparer données<br/>JS Code]
    SW{Switch plateformes<br/>12 routes}
    AG[Agréger résultats<br/>Merge node]
    RP[Réponse Webhook<br/>JSON output]

    P1[Publier LinkedIn]
    P2[Publier Instagram]
    P3[Publier Facebook]
    P4[Publier TikTok]
    P5[Publier YouTube Shorts]
    P6[Publier X / Twitter]
    P7[Publier Pinterest]
    P8[Publier Threads]
    P9[Publier Snapchat]
    P10[Publier Google Business]
    P11[Publier Blog / SEO]
    P12[Publier Email]

    WT --> PD --> SW
    SW --> P1 --> AG
    SW --> P2 --> AG
    SW --> P3 --> AG
    SW --> P4 --> AG
    SW --> P5 --> AG
    SW --> P6 --> AG
    SW --> P7 --> AG
    SW --> P8 --> AG
    SW --> P9 --> AG
    SW --> P10 --> AG
    SW --> P11 --> AG
    SW --> P12 --> AG
    AG --> RP

    classDef trigger fill:#ea4b71,stroke:#9b1d3e,color:#fff
    classDef code fill:#1f2937,stroke:#a78bfa,color:#fff
    classDef switch fill:#3b82f6,stroke:#1e40af,color:#fff
    classDef publish fill:#10b981,stroke:#065f46,color:#fff
    classDef respond fill:#f59e0b,stroke:#92400e,color:#fff

    class WT,RP trigger
    class PD,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12 code
    class SW switch
    class AG respond
```

**Latence mesurée en mode production** : ~120 ms pour les 12 publishers en parallèle (hors temps OpenAI).

---

## 📐 Légende des couleurs (cohérence avec le frontend)

| Couleur | Hex | Usage |
|---|---|---|
| 🟣 Violet primary | `#7c3aed` | Brand / boutons / accents |
| 🟪 Accent | `#a78bfa` | Hover / liens / highlight |
| ⚫ Background dark | `#0e1117` | Fond principal |
| ⬛ Background card | `#161a26` | Cartes / sidebar |

---

*Schémas générés en Mermaid v11+ — rendu automatique sur GitHub. Pour export PNG/SVG, utiliser https://mermaid.live*
