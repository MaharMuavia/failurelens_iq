from __future__ import annotations

BLAME_PHRASES = [
    "engineer failed",
    "developer mistake",
    "person responsible",
    "individual error",
    "fault",
    "your mistake",
    "you failed",
]


def contains_blame_language(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in BLAME_PHRASES)


def safe_process_language(text: str) -> str:
    replacements = {
        "engineer failed": "team process gap appeared",
        "developer mistake": "team process gap",
        "person responsible": "team review owner",
        "individual error": "systematic knowledge gap",
        "fault": "contributing process gap",
        "your mistake": "team learning opportunity",
        "you failed": "the process did not provide enough support",
    }
    safe = text
    for phrase, replacement in replacements.items():
        safe = safe.replace(phrase, replacement)
        safe = safe.replace(phrase.title(), replacement)
    return safe
