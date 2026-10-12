from __future__ import annotations


def _walk(value, path="root"):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def find_components(registry, keywords: list[str]) -> list[dict]:
    terms = [str(term).strip().lower() for term in keywords if str(term).strip()]
    matches = []
    seen = set()

    for path, row in _walk(registry):
        text = " ".join(str(v) for v in row.values() if isinstance(v, (str, int, float, bool))).lower()
        score = sum(1 for term in terms if term in text)
        if not score:
            continue
        identity = (
            str(row.get("id") or row.get("name") or row.get("component") or path),
            path,
        )
        if identity in seen:
            continue
        seen.add(identity)
        matches.append({
            "path": path,
            "score": score,
            "component": row,
        })

    matches.sort(key=lambda item: (-item["score"], item["path"]))
    return matches
