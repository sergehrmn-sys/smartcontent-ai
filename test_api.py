"""Smoke tests for SmartContent AI backend.

Usage (with backend running on http://localhost:8001):
    python test_api.py
"""
from __future__ import annotations

import json
import sys
import time
from typing import Any

import requests

API = "http://localhost:8001"


def _print(title: str, ok: bool, body: Any = None) -> None:
    icon = "✅" if ok else "❌"
    print(f"{icon} {title}")
    if body is not None:
        try:
            print(json.dumps(body, indent=2, ensure_ascii=False)[:400])
        except Exception:
            print(str(body)[:400])
    print()


def test_health() -> bool:
    r = requests.get(f"{API}/health", timeout=5)
    ok = r.ok and r.json().get("status") == "ok"
    _print("/health", ok, r.json() if r.ok else r.text)
    return ok


def test_register_login() -> str | None:
    suffix = int(time.time())
    email = f"test_{suffix}@smartcontent.dev"
    pw = "test123!"
    r = requests.post(
        f"{API}/auth/register",
        json={"email": email, "password": pw, "nom_entreprise": "TestCo", "plan": "free"},
        timeout=15,
    )
    ok_reg = r.ok
    _print(f"/auth/register ({email})", ok_reg, r.json() if r.ok else r.text)
    if not ok_reg:
        return None

    user_id = r.json()["user_id"]

    r2 = requests.post(
        f"{API}/auth/login",
        json={"email": email, "password": pw},
        timeout=10,
    )
    _print("/auth/login", r2.ok, r2.json() if r2.ok else r2.text)
    return user_id if r2.ok else None


def test_generate(user_id: str | None) -> bool:
    payload = {
        "user_id": user_id,
        "sujet": "Lancement de notre application IA pour PME",
        "secteur": "tech",
        "ton": "professionnel",
        "objectif": "annoncer",
        "plateformes": ["linkedin", "tiktok"],
    }
    r = requests.post(f"{API}/generate/", json=payload, timeout=120)
    ok = r.ok
    body = r.json() if r.ok else r.text
    _print("/generate/", ok, body)
    return ok


def test_history(user_id: str | None) -> bool:
    if not user_id:
        return False
    r = requests.get(f"{API}/history/{user_id}", timeout=10)
    _print(f"/history/{user_id}", r.ok, r.json() if r.ok else r.text)
    return r.ok


def main() -> int:
    print(f"=== SmartContent AI — smoke test ({API}) ===\n")
    if not test_health():
        print("Backend KO — abort.")
        return 1
    user_id = test_register_login()
    test_generate(user_id)
    test_history(user_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
