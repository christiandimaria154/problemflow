from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_PATH = ROOT / "data" / "problems.json"
CURRENT_PATH = ROOT / "current.json"
STATE_PATH = ROOT / "state.json"

VALID_SLOTS = {"lunedi", "giovedi"}
VALID_CLASSES = {"3C", "4C"}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return default
    return json.loads(text)


def save_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_slot(raw: str | None) -> str:
    slot = (raw or "").strip().lower()
    if slot not in VALID_SLOTS:
        raise ValueError(f"Slot non valido: {slot!r}")
    return slot


def normalize_class(raw: str | None) -> str:
    cls = (raw or "").strip().upper()
    if cls not in VALID_CLASSES:
        raise ValueError(f"Classe non valida: {cls!r}")
    return cls


def default_current() -> dict[str, Any]:
    return {
        "3C": {"lunedi": None, "giovedi": None},
        "4C": {"lunedi": None, "giovedi": None},
        "updated_at": None,
    }


def default_state() -> dict[str, Any]:
    return {
        "history": {
            "3C": [],
            "4C": [],
        }
    }


def validate_problems(raw_problems: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_problems, list):
        raise ValueError("data/problems.json deve contenere un array JSON")

    validated: list[dict[str, Any]] = []

    for idx, item in enumerate(raw_problems, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Problema #{idx}: atteso oggetto JSON")

        cls = normalize_class(item.get("class_code"))
        pref = (item.get("preferred_slot") or "any").strip().lower()
        if pref not in {"lunedi", "giovedi", "any"}:
            raise ValueError(
                f"Problema {item.get('id', idx)!r}: preferred_slot non valido: {pref!r}"
            )

        if not item.get("id"):
            raise ValueError(f"Problema #{idx}: campo 'id' mancante")
        if not item.get("title"):
            raise ValueError(f"Problema {item['id']!r}: campo 'title' mancante")
        if not item.get("body"):
            raise ValueError(f"Problema {item['id']!r}: campo 'body' mancante")
        if not item.get("topic"):
            raise ValueError(f"Problema {item['id']!r}: campo 'topic' mancante")
        if not item.get("difficulty"):
            raise ValueError(f"Problema {item['id']!r}: campo 'difficulty' mancante")

        validated.append(
            {
                "id": str(item["id"]),
                "class_code": cls,
                "language": str(item.get("language", "")).strip(),
                "topic": str(item["topic"]).strip(),
                "difficulty": str(item["difficulty"]).strip(),
                "preferred_slot": pref,
                "title": str(item["title"]).strip(),
                "body": str(item["body"]).strip(),
                "active": bool(item.get("active", True)),
            }
        )

    return validated


def choose_problem(
    problems: list[dict[str, Any]],
    state: dict[str, Any],
    class_code: str,
    slot: str,
) -> dict[str, Any]:
    history = state.setdefault("history", {}).setdefault(class_code, [])

    candidates = [
        p
        for p in problems
        if p["active"]
        and p["class_code"] == class_code
        and p["preferred_slot"] in {slot, "any"}
    ]

    if not candidates:
        raise ValueError(f"Nessun problema disponibile per {class_code} / {slot}")

    candidates.sort(key=lambda p: p["id"])
    unused = [p for p in candidates if p["id"] not in history]

    if not unused:
        history.clear()
        unused = candidates[:]

    chosen = unused[0]
    history.append(chosen["id"])
    return chosen


def to_current_item(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": problem["id"],
        "topic": problem["topic"],
        "difficulty": problem["difficulty"],
        "title": problem["title"],
        "body": problem["body"],
    }


def main() -> None:
    slot = normalize_slot(os.getenv("FORCE_SLOT"))
    problems = validate_problems(load_json(PROBLEMS_PATH, []))
    current = load_json(CURRENT_PATH, default_current())
    state = load_json(STATE_PATH, default_state())

    if not isinstance(current, dict):
        current = default_current()
    if not isinstance(state, dict):
        state = default_state()

    for class_code in ("3C", "4C"):
        chosen = choose_problem(problems, state, class_code, slot)
        current.setdefault(class_code, {})[slot] = to_current_item(chosen)

    current["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    save_json(CURRENT_PATH, current)
    save_json(STATE_PATH, state)


if __name__ == "__main__":
    main()
