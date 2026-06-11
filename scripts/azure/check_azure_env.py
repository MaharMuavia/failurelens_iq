from __future__ import annotations

from azure_env import env


def mark(name: str, required: bool = True) -> str:
    value = env(name)
    status = "OK" if value else ("MISSING" if required else "optional")
    return f"[{status}] {name}"


def main() -> int:
    print("FailureLens IQ Azure environment checklist")
    for name in ["AZURE_AI_SEARCH_ENDPOINT", "AZURE_AI_SEARCH_KEY", "AZURE_AI_SEARCH_INDEX"]:
        print(mark(name, required=True))
    for name in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"]:
        print(mark(name, required=False))
    missing = [name for name in ["AZURE_AI_SEARCH_ENDPOINT", "AZURE_AI_SEARCH_KEY", "AZURE_AI_SEARCH_INDEX"] if not env(name)]
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
