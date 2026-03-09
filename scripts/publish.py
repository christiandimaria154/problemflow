#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_FILE = os.path.join(BASE_DIR, "data", "problems.json")
STATE_FILE = os.path.join(BASE_DIR, "data", "state.json")
CURRENT_FILE = os.path.join(BASE_DIR, "current.json")
VALID_SLOTS = {"lunedi", "giovedi"}

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def detect_slot():
    force_slot = os.environ.get("FORCE_SLOT", "").strip().lower()
    if force_slot in VALID_SLOTS:
        return force_slot
    now = datetime.now(timezone.utc)
    if now.weekday() == 0:
        return "lunedi"
    if now.weekday() == 3:
        return "giovedi"
    raise SystemExit("Oggi non è né lunedì né giovedì. Usa FORCE_SLOT=lunedi oppure FORCE_SLOT=giovedi.")

def week_key():
    now = datetime.now(timezone.utc)
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"

def select_problem(problems, state, class_code, slot):
    used = state["used_ids"][class_code][slot]
    candidates = [p for p in problems if p["class_code"] == class_code and p["preferred_slot"] in (slot, "any")]
    fresh = [p for p in candidates if p["id"] not in used]
    if not fresh:
        state["used_ids"][class_code][slot] = []
        fresh = candidates
    if not fresh:
        raise SystemExit(f"Nessun problema disponibile per {class_code} - {slot}")
    chosen = fresh[0]
    state["used_ids"][class_code][slot].append(chosen["id"])
    state["history"].append({
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "week_key": week_key(),
        "class_code": class_code,
        "slot": slot,
        "problem_id": chosen["id"]
    })
    return chosen

def main():
    slot = detect_slot()
    problems = load_json(PROBLEMS_FILE)
    state = load_json(STATE_FILE)
    try:
        current = load_json(CURRENT_FILE)
    except FileNotFoundError:
        current = {"3C": {}, "4C": {}}

    for class_code in ("3C", "4C"):
        current.setdefault(class_code, {})
        current[class_code][slot] = select_problem(problems, state, class_code, slot)

    current["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    current["week_key"] = week_key()

    save_json(STATE_FILE, state)
    save_json(CURRENT_FILE, current)
    print(f"Pubblicazione completata per slot: {slot}")

if __name__ == "__main__":
    main()
