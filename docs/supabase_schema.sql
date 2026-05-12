-- =============================================================================
-- SmartContent AI — Supabase schema
-- =============================================================================
-- Run this in Supabase Studio → SQL Editor → New query → Run.
-- Required: pgcrypto for gen_random_uuid().
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- USERS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email            TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    nom_entreprise   TEXT,
    plan             TEXT NOT NULL DEFAULT 'free',
    date_inscription TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users (email);

-- ---------------------------------------------------------------------------
-- CONTENTS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.contents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES public.users(id) ON DELETE CASCADE,
    sujet         TEXT NOT NULL,
    secteur       TEXT,
    ton           TEXT,
    objectif      TEXT,
    type_contenu  TEXT,
    plateformes   JSONB NOT NULL DEFAULT '[]'::jsonb,
    content       JSONB NOT NULL DEFAULT '{}'::jsonb,
    images        JSONB NOT NULL DEFAULT '{}'::jsonb,
    statut        TEXT NOT NULL DEFAULT 'draft',  -- draft | publie | erreur
    date_creation TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Migration safety net: if you already ran an earlier version of this schema
-- without `type_contenu`, this adds the column without breaking existing rows.
ALTER TABLE public.contents ADD COLUMN IF NOT EXISTS type_contenu TEXT;
ALTER TABLE public.contents ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_contents_user_id      ON public.contents (user_id);
CREATE INDEX IF NOT EXISTS idx_contents_date_creation ON public.contents (date_creation DESC);

-- ---------------------------------------------------------------------------
-- ⚠️ Disable Row Level Security on both tables
-- The backend uses the SERVICE-ROLE key (bypasses RLS) but we disable RLS to
-- avoid silent failures during dev/MVP.
-- ---------------------------------------------------------------------------
ALTER TABLE public.users    DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.contents DISABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------