from __future__ import annotations

import re


STOP_WORDS = {"the", "and", "for", "with", "from", "new", "set", "pack"}


def generate_keywords(candidate: dict, *, max_keywords: int = 5) -> list[str]:
    parts = [
        str(candidate.get("name") or ""),
        str(candidate.get("category") or ""),
        str((candidate.get("metadata") or {}).get("brand") or ""),
        str((candidate.get("metadata") or {}).get("sku") or ""),
    ]
    tokens = []
    for part in parts:
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}", part.lower()):
            if token in STOP_WORDS or token in tokens:
                continue
            tokens.append(token)
    phrases = []
    name = re.sub(r"s+", " ", str(candidate.get("name") or "")).strip()
    if name:
        phrases.append(name[:120])
    phrases.extend(tokens)
    return phrases[:max(1, int(max_keywords))]
