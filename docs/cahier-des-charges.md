# Cahier des charges — SmartContent AI

| | |
|---|---|
| **Projet** | SmartContent AI |
| **Type** | Application SaaS de génération et publication automatique de contenu marketing IA multi-plateformes |
| **Auteur** | Serge Tsebo |
| **Formation** | AEC Intelligence Artificielle Appliquée |
| **Établissement** | Collège Multihexa, Montréal (Québec) |
| **Date** | Mai 2026 |
| **Version** | 1.0 |

---

## Sommaire

1. Présentation du projet
2. Contexte et problématique
3. Objectifs
4. Cible utilisateur
5. Périmètre du projet
6. Spécifications fonctionnelles
7. Spécifications techniques
8. Contraintes
9. Livrables
10. Planning et jalons
11. Critères d'acceptation
12. Risques et mitigation
13. Annexes

---

## 1. Présentation du projet

### 1.1 Description courte

SmartContent AI est une application web qui permet à un utilisateur de créer une campagne marketing complète à partir d'une **seule idée saisie en quelques mots**. L'intelligence artificielle se charge ensuite de :

- Adapter automatiquement le texte à **12 plateformes** (LinkedIn, Instagram, Facebook, TikTok, YouTube Shorts, X / Twitter, Pinterest, Threads, Snapchat, Google Business Profile, Blog SEO, Email marketing) en respectant les codes éditoriaux de chacune.
- Générer **3 visuels haute qualité** (formats carré, paysage, portrait) prêts à publier.
- Orchestrer la **publication multi-plateformes** via un workflow d'automatisation n8n.

L'objectif est de réduire de **plusieurs heures à moins de deux minutes** le temps nécessaire pour produire et publier une campagne marketing complète.

### 1.2 Slogan

> **Créez. Automatisez. Publiez.**
> Une idée, douze posts, en moins d'une minute.

---

## 2. Contexte et problématique

### 2.1 Contexte du marché

Le marché québécois compte plus de **245 000 PME** (Statistique Canada, 2024). La majorité d'entre elles — restaurants, salons d'esthétique, garages automobiles, immobilier, coachs, créateurs de contenu — souhaitent être visibles sur les réseaux sociaux pour acquérir et fidéliser leur clientèle. Cependant :

- **62 % des PME québécoises** déclarent ne pas avoir le temps de gérer leurs réseaux sociaux régulièrement (étude Léger Marketing, 2024).
- **38 %** estiment que produire du contenu de qualité représente un obstacle majeur.
- **Le coût d'une agence marketing** pour une PME oscille entre **1 500 $ et 4 000 $ CAD par mois**, ce qui est inaccessible pour la plupart.

### 2.2 Problématique

> *Comment permettre à une PME québécoise de produire et publier du contenu marketing professionnel adapté à plus de 10 plateformes sociales, en quelques minutes, et pour moins d'un dollar par campagne ?*

### 2.3 Justification du projet

Le développement récent des modèles de langage (GPT-4o) et de génération d'image (DALL-E 3) rend cette automatisation à la fois **techniquement faisable** et **économiquement viable**. SmartContent AI exploite ces APIs pour offrir une solution clé en main, accessible et scalable.

---

## 3. Objectifs

### 3.1 Objectif général

Concevoir, développer et déployer une application web fonctionnelle qui automatise la chaîne complète **idée → contenu adapté → visuels → publication multi-plateformes**, en exploitant l'intelligence artificielle générative.

### 3.2 Objectifs spécifiques

| # | Objectif | Critère mesurable |
|---|---|---|
| O1 | Authentifier les utilisateurs de manière sécurisée | Mots de passe hashés bcrypt, JWT pour la session |
| O2 | Générer du contenu textuel personnalisé | 12 plateformes supportées avec prompts dédiés |
| O3 | Adapter le contenu aux paramètres utilisateur | 15 tons, 15 objectifs, 37 secteurs, 12 types de contenu |
| O4 | Produire des visuels prêts à publier | 3 formats DALL-E 3 par campagne (1:1, 16:9, 9:16) |
| O5 | Orchestrer la publication automatisée | Workflow n8n avec 12 publishers parallèles |
| O6 | Persister l'historique des campagnes | Base PostgreSQL Supabase avec colonnes JSONB |
| O7 | Offrir une interface utilisateur intuitive | 6 pages Streamlit avec thème violet professionnel |
| O8 | Permettre l'export et la gestion de l'historique | Filtres, recherche, modifier-régénérer, supprimer, export CSV |

### 3.3 Objectifs pédagogiques

Ce projet permet à l'étudiant de mettre en pratique les compétences acquises lors de l'AEC :

- Conception et développement d'une **architecture client-serveur** moderne (FastAPI + Streamlit).
- Intégration d'**APIs d'intelligence artificielle** (OpenAI GPT-4o + DALL-E 3).
- Modélisation et gestion d'une **base de données relationnelle** (PostgreSQL via Supabase).
- Mise en œuvre de **bonnes pratiques de sécurité** (bcrypt, JWT, RLS, .env, .gitignore).
- Maîtrise d'un outil de **workflow automation** (n8n).
- Pratique du **versionnement Git** et de la documentation technique.

---

## 4. Cible utilisateur

### 4.1 Personas

**Persona 1 — Marie, propriétaire de salon de coiffure**
Marie, 38 ans, gère seule un salon à Montréal. Elle veut publier 3 posts par semaine sur Instagram, Facebook et Google Business Profile mais n'a ni le temps ni les compétences en design. Aujourd'hui, elle paie un community manager freelance 800 $/mois.

> *Avec SmartContent AI, Marie crée 3 campagnes complètes par semaine en moins de 10 minutes, pour environ 0,70 $ CAD par semaine.*

**Persona 2 — David, agent immobilier**
David, 45 ans, doit promouvoir 5 propriétés différentes par mois sur LinkedIn, Facebook, Pinterest et son blog. Il ne sait pas écrire pour le SEO et n'a pas de visuels professionnels.

**Persona 3 — Sophie, créatrice de contenu**
Sophie, 28 ans, est consultante freelance. Elle veut maintenir une présence forte sur LinkedIn, Threads et X mais consacre déjà 80 % de son temps à ses clients.

### 4.2 Marché potentiel

- **Cible primaire** : PME québécoises de 1 à 50 employés (≈ 200 000 entreprises).
- **Cible secondaire** : agences marketing locales souhaitant gérer plusieurs clients.
- **Cible tertiaire** : créateurs de contenu solo et entrepreneurs individuels.

---

## 5. Périmètre du projet

### 5.1 Inclus dans le MVP (Minimum Viable Product)

✅ Authentification utilisateur (inscription + connexion)
✅ Génération de texte multi-plateformes (12 plateformes)
✅ Génération d'images IA (3 formats)
✅ Génération de hashtags globaux pertinents
✅ Personnalisation par secteur, ton, objectif, type de contenu
✅ Tableau de bord avec métriques
✅ Historique avec filtres avancés (statut, plateforme), recherche, modifier, supprimer, export CSV
✅ Workflow n8n d'orchestration multi-plateformes (mode simulé pour le MVP)
✅ Persistance Supabase complète
✅ Interface utilisateur soignée (thème violet, logo SVG, footer académique)

### 5.2 Hors périmètre (Phase 2 — post-soutenance)

❌ Publication réelle sur LinkedIn / Meta / TikTok (nécessite approbation des APIs : 4-8 semaines)
❌ Programmation des posts (calendrier marketing)
❌ Génération de vidéo IA (Runway / Veo + ElevenLabs voix off)
❌ Analyse des performances (likes, vues, clics)
❌ Gestion multi-entreprises (mode agence)
❌ Application mobile native ou PWA
❌ Système de paiement Stripe (mode commercial)
❌ Conformité Loi 25 / RGPD complète

---

## 6. Spécifications fonctionnelles

### 6.1 Modules fonctionnels

#### M1 — Module d'authentification
- **F1.1** Inscription par email + mot de passe + nom d'entreprise + plan (free/pro/premium)
- **F1.2** Connexion avec validation bcrypt
- **F1.3** Génération d'un JWT à durée de vie 24h (1440 min)
- **F1.4** Détection des doublons (email déjà existant → HTTP 409)
- **F1.5** Déconnexion (réinitialisation de la session)

#### M2 — Module de génération
- **F2.1** Formulaire avec 5 champs : sujet (texte libre), secteur (37 options), ton (15 options), objectif (15 options), type de contenu (12 options)
- **F2.2** Sélection de 1 à 12 plateformes via cases à cocher
- **F2.3** Appel parallèle à GPT-4o pour chaque plateforme avec prompt dédié
- **F2.4** Génération de 12 hashtags globaux par appel GPT-4o séparé
- **F2.5** Génération de 3 images DALL-E 3 en parallèle (formats 1:1, 16:9, 9:16)
- **F2.6** Affichage des résultats en onglets par plateforme (texte + nombre de mots + hashtags + CTA)
- **F2.7** Sauvegarde automatique dans la base de données

#### M3 — Module de publication
- **F3.1** Bouton « Envoyer au workflow n8n »
- **F3.2** Appel POST vers le webhook n8n avec le payload complet (textes + images)
- **F3.3** Mise à jour automatique du statut en base (`draft` → `publie`)
- **F3.4** Workflow n8n distribuant le contenu vers 12 publishers (simulés)

#### M4 — Module Tableau de bord
- **F4.1** 3 métriques : nombre de contenus créés, publiés, en draft
- **F4.2** Graphique de répartition par plateforme
- **F4.3** Liste des 5 derniers contenus
- **F4.4** Section « Fonctionnalités à venir » avec 10 badges grisés (roadmap)

#### M5 — Module Historique
- **F5.1** Liste expansible de tous les contenus de l'utilisateur
- **F5.2** Filtre par statut (Tous / draft / publié)
- **F5.3** Filtre par plateforme (12 options)
- **F5.4** Recherche par mot-clé dans le sujet
- **F5.5** Bouton « Modifier & régénérer » (charge les paramètres dans le générateur)
- **F5.6** Bouton « Supprimer » avec confirmation à deux étapes
- **F5.7** Export CSV de l'historique filtré

#### M6 — Module Paramètres et n8n Status
- **F6.1** Affichage des informations du compte (email, ID, entreprise, plan)
- **F6.2** Affichage des URLs API et webhook n8n
- **F6.3** Bouton « Ping de test » du webhook n8n
- **F6.4** Guide de configuration n8n

### 6.2 Diagramme de cas d'utilisation (UML)

```
                ┌────────────────────────────────────┐
                │         SmartContent AI            │
                │                                    │
                │  ◯ S'inscrire                       │
                │  ◯ Se connecter                     │
                │  ◯ Générer une campagne             │
                │  ◯ Publier une campagne (n8n)       │
                │  ◯ Consulter l'historique           │
                │  ◯ Filtrer / rechercher             │
                │  ◯ Modifier & régénérer             │
                │  ◯ Supprimer un contenu             │
                │  ◯ Exporter en CSV                  │
                │  ◯ Consulter le tableau de bord     │
                │                                    │
                └────────────────────────────────────┘
                         ▲
                         │
                    ┌────┴────┐
                    │ Utilisateur
                    │ (PME)   │
                    └─────────┘
```

---

## 7. Spécifications techniques

### 7.1 Architecture globale

Architecture **3-tiers** découplée avec des services externes :

```
[Streamlit 8501] ↔ [FastAPI 8001] ↔ [Supabase PostgreSQL]
                          ↓
                   [OpenAI GPT-4o + DALL-E 3]
                          ↓
                   [n8n Webhook 5678]
```

Voir `docs/architecture.md` pour les diagrammes détaillés (Mermaid).

### 7.2 Stack technique

#### Backend
- **Python 3.14**
- **FastAPI 0.136** (framework web async, OpenAPI auto-généré)
- **Pydantic v2** + **pydantic-settings** (validation et configuration)
- **python-jose** (JWT)
- **bcrypt 5.0** (hash de mots de passe)
- **supabase-py 2.30** (client Supabase service-role)
- **openai 2.35** (SDK officiel OpenAI)
- **httpx** (client HTTP async pour n8n)
- **uvicorn** (serveur ASGI)

#### Frontend
- **Streamlit 1.57** (framework UI Python)
- Thème personnalisé (`primaryColor = #7c3aed`)
- CSS injecté pour boutons gradient violet, cartes métriques, footer
- SVG inline pour le logo brandé

#### Base de données
- **Supabase** (PostgreSQL 15 hébergé)
- Tables : `users`, `contents`
- Colonnes JSONB pour `plateformes`, `content`, `images`
- Index sur `email`, `user_id`, `date_creation DESC`
- RLS désactivé pour le MVP (backend utilise la service-role key)

#### Intelligence artificielle
- **OpenAI GPT-4o** : génération de texte adaptée par plateforme + génération de hashtags
- **OpenAI DALL-E 3** : génération de 3 images en parallèle (ThreadPoolExecutor)
- Prompt engineering : prompts dédiés par plateforme (longueur, ton, hashtags, CTA)

#### Automatisation
- **n8n Desktop** (version locale du workflow automation)
- Workflow : Webhook Trigger → Code (préparation) → Switch (12 routes) → 12 Code nodes (publishers) → Merge → Respond Webhook
- Mode production (`/webhook/`) avec workflow Published

### 7.3 Sécurité

| Aspect | Implémentation |
|---|---|
| Mots de passe | Hashés avec **bcrypt** (cost 12, salt aléatoire) |
| Sessions | **JWT** signés HS256, expiration 24h |
| Variables sensibles | Stockées dans **`.env`** local, exclu de Git via `.gitignore` |
| Clés Supabase | **Service-role** côté backend uniquement, jamais exposée au client |
| RLS | Désactivé MVP, à réactiver en production avec policies par `user_id` |
| HTTPS | À activer en production via reverse proxy (Render / Vercel) |
| CORS | Configuré pour `localhost:8501`, `localhost:3000` (dev) |

### 7.4 Performance

| Opération | Latence mesurée |
|---|---|
| Génération texte 1 plateforme | ~3-5 s (GPT-4o) |
| Génération 12 plateformes (séquentiel) | ~40-60 s |
| Génération 12 hashtags globaux | ~2-3 s |
| Génération 3 images DALL-E (parallèle) | ~15-20 s |
| Requête `/history/{user_id}` | ~50-100 ms |
| Webhook n8n (production) | ~120 ms (12 publishers parallèles) |
| **Campagne complète (texte + images + persistance)** | **60-90 s** |

---

## 8. Contraintes

### 8.1 Contraintes techniques

- **Python 3.14** est la version cible. Les bibliothèques `pillow`, `moviepy`, `pydantic-core` (pinné) sont incompatibles → exclues du `requirements.txt`.
- **OpenAI** impose une limite de débit (rate limit) qui peut être atteinte en cas d'utilisation intensive. Mitigation : retry automatique côté SDK.
- **DALL-E 3** : URLs valides 60 minutes uniquement. Mitigation phase 2 : upload Supabase Storage pour persistance.
- **n8n** : workflow Published obligatoire pour le mode production ; sinon mode test (un appel par clic).

### 8.2 Contraintes budgétaires

| Item | Coût par campagne |
|---|---|
| OpenAI GPT-4o (12 prompts texte) | ~0,05 $ CAD |
| OpenAI GPT-4o (12 hashtags globaux) | ~0,005 $ CAD |
| OpenAI DALL-E 3 (3 images standard) | ~0,16 $ CAD |
| Supabase (Free tier : 500 MB DB, 1 GB storage) | 0 $ CAD |
| n8n Desktop | 0 $ CAD |
| **Coût total par campagne** | **~0,22 $ CAD** |

Coût mensuel estimé pour un utilisateur générant 30 campagnes : **6,60 $ CAD**. Marge confortable pour un plan SaaS à 29 $/mois.

### 8.3 Contraintes calendaires

- **Démarrage** : avril 2026
- **Soutenance** : fin mai 2026
- **Durée totale** : ~6 semaines

### 8.4 Contraintes légales (Québec)

- **Loi 25** (équivalent québécois du RGPD) : politique de confidentialité requise pour la mise en production. À traiter en phase 2.
- **TPS / TVQ** : applicable au-delà de 30 000 $ de chiffre d'affaires annuel.
- **Conditions d'utilisation** des APIs OpenAI et n8n respectées.

---

## 9. Livrables

| # | Livrable | Format | Statut |
|---|---|---|---|
| L1 | Code source du projet | Repository Git public/privé | ✅ Livré (`github.com/sergehrmn-sys/smartcontent-ai`) |
| L2 | Application fonctionnelle | Localhost (backend + frontend + n8n) | ✅ Livré |
| L3 | Schéma de base de données SQL | `docs/supabase_schema.sql` | ✅ Livré |
| L4 | Schémas UML / architecture | `docs/architecture.md` (Mermaid) | ✅ Livré |
| L5 | Cahier des charges | `docs/cahier-des-charges.md` (présent document) | ✅ Livré |
| L6 | Mémoire écrit | `.docx` 25-35 pages | 🔄 En cours |
| L7 | Présentation soutenance | `.pptx` 12-15 slides | ⏳ À faire |
| L8 | Vidéo démonstration | `.mp4` 2-3 minutes | ⏳ À faire |

---

## 10. Planning et jalons

### Phases du projet

| Phase | Période | Livrables clés |
|---|---|---|
| **Phase 1 — Conception** | Semaine 1 | Cahier des charges, schémas UML, choix de la stack |
| **Phase 2 — MVP fonctionnel** | Semaines 2-3 | Backend FastAPI, frontend Streamlit, auth, génération texte |
| **Phase 3 — Enrichissement** | Semaine 4 | Images DALL-E, n8n workflow, persistance Supabase |
| **Phase 4 — Polish** | Semaine 5 | Thème violet, historique avancé, filtres, export CSV |
| **Phase 5 — Documentation** | Semaine 6 | Mémoire, slides, vidéo démo, push GitHub final |
| **Phase 6 — Soutenance** | Fin mai 2026 | Défense orale + démonstration live |

### Diagramme de Gantt simplifié

```
S1: ████ Conception
S2:     ████ Backend + Auth
S3:         ████ Génération multi-plateformes
S4:             ████ Images + n8n + Supabase
S5:                 ████ Historique + Polish UI
S6:                     ████ Documentation
                            🎯 Soutenance
```

---

## 11. Critères d'acceptation

### 11.1 Tests fonctionnels

| ID | Test | Critère de réussite |
|---|---|---|
| T1 | Inscription d'un nouvel utilisateur | Compte créé, JWT retourné, redirection vers Générateur |
| T2 | Connexion avec mot de passe correct | JWT retourné, accès aux pages protégées |
| T3 | Connexion avec mot de passe incorrect | HTTP 401, pas d'accès |
| T4 | Génération avec 4 plateformes cochées | 4 onglets de résultats + 3 images affichés |
| T5 | Génération avec 12 plateformes | 12 onglets, 3 images, durée < 90 s |
| T6 | Sauvegarde Supabase | Ligne créée dans `contents` avec tous les champs remplis |
| T7 | Filtre Historique par statut | Liste filtrée correctement |
| T8 | Suppression d'un contenu | Confirmation à deux étapes, ligne disparaît, status 200 |
| T9 | Export CSV | Fichier téléchargé avec colonnes correctes |
| T10 | Webhook n8n (mode production) | Statut HTTP 200, exécution visible dans onglet Executions |

### 11.2 Tests non fonctionnels

- L'application doit démarrer en moins de 10 secondes (uvicorn + streamlit).
- Le `.env` ne doit jamais apparaître dans le repository GitHub (vérifié via `git ls-files`).
- Aucune dépendance Python ne doit afficher d'erreur de compilation lors du `pip install`.
- L'interface doit s'afficher correctement sur écran 1920x1080 et 1366x768.

---

## 12. Risques et mitigation

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| OpenAI rate limit pendant la démo soutenance | Moyenne | Élevé | Tests préalables, génération de contenus en avance |
| n8n Desktop crashe pendant la démo | Faible | Moyen | Mode test fallback (`webhook-test/`) qui marche toujours |
| Connexion Supabase coupée | Faible | Élevé | Backend log les erreurs, refresh manuel |
| OneDrive corrompt des fichiers à l'écriture | Élevée | Moyen | Écriture via `cat > ... << EOF` (atomique) |
| Bug dernière minute non détecté | Moyenne | Élevé | Tests fonctionnels exhaustifs en phase 5 |
| Retard sur la rédaction du mémoire | Moyenne | Élevé | Réutilisation maximale des sections du cahier des charges |

---

## 13. Annexes

### 13.1 Glossaire

| Terme | Définition |
|---|---|
| **API REST** | Interface de programmation suivant l'architecture REST (HTTP + JSON) |
| **bcrypt** | Algorithme de hash de mot de passe résistant aux attaques par dictionnaire |
| **CTA** | Call-to-action (appel à l'action) |
| **DALL-E 3** | Modèle de génération d'image d'OpenAI |
| **GPT-4o** | Modèle de langage multimodal d'OpenAI |
| **JSONB** | Type PostgreSQL pour stocker du JSON binaire indexable |
| **JWT** | JSON Web Token, format de jeton signé pour l'authentification |
| **MVP** | Minimum Viable Product (produit minimum viable) |
| **n8n** | Plateforme open-source d'automatisation de workflows |
| **PME** | Petite ou moyenne entreprise |
| **PWA** | Progressive Web App |
| **RLS** | Row Level Security (sécurité au niveau de la ligne PostgreSQL) |
| **Supabase** | Plateforme BaaS (Backend-as-a-Service) basée sur PostgreSQL |
| **Webhook** | Endpoint HTTP appelé automatiquement par un système tiers |

### 13.2 Références

- [Documentation FastAPI](https://fastapi.tiangolo.com)
- [Documentation Streamlit](https://docs.streamlit.io)
- [Documentation Supabase](https://supabase.com/docs)
- [Documentation OpenAI API](https://platform.openai.com/docs)
- [Documentation n8n](https://docs.n8n.io)
- Statistique Canada — *Statistiques sur les PME au Québec* (2024)
- Léger Marketing — *Étude sur la présence numérique des PME* (2024)

### 13.3 Contact

| | |
|---|---|
| **Auteur** | Serge Tsebo |
| **Email** | sergehrmn@gmail.com |
| **Repository** | https://github.com/sergehrmn-sys/smartcontent-ai |
| **Établissement** | Collège Multihexa, Montréal, Québec |

---

*Document v1.0 — Mai 2026*
