from __future__ import annotations
import os, time
from typing import Dict
from hashlib import sha256, new as hmac_new
from hmac import compare_digest
from fastapi import HTTPException, status

BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
SECRET_KEY: bytes = sha256(BOT_TOKEN.encode()).digest()
MAX_AGE = 5 * 60  # 5 минут

def _calc_hash(payload: Dict[str, str]) -> str:
    data_check = "\n".join(f"{k}={payload[k]}" for k in sorted(payload) if k != "hash")
    return hmac_new(SECRET_KEY, data_check.encode(), sha256).hexdigest()

def verify(payload: Dict[str, str]) -> Dict[str, str]:
    if "hash" not in payload:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "hash missing")
    if not compare_digest(_calc_hash(payload), payload["hash"]):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "invalid hash")
    if time.time() - int(payload["auth_date"]) > MAX_AGE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "login expired")
    return payload
