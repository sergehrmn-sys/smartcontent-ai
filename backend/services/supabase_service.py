"""Supabase client.

CRITICAL: backend uses the SERVICE-ROLE key (supabase_secret) so writes/reads
bypass RLS. The publishable key (supabase_key) would be blocked by RLS.
"""
from supabase import create_client, Client

from backend.config import settings

# ⚠️ DO NOT replace `supabase_secret` with `supabase_key` here.
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_secret)
