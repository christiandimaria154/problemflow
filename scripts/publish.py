#!/usr/bin/env python3
import json
import os
import random
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_FILE = os.path.join(ROOT, 'data', 'problems.json')
CURRENT_FILE = os.path.join(ROOT, 'current.json')
STATE_FILE = os.path.join(ROOT, 'state.json')

CLASS_CODES = ['3C', '4C']
SLOTS = ['lunedi', 'giovedi']


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def detect_slot():
    # Monday=0, Thursday=3
    weekday = datetime.now(timezone.utc).weekday()
    if weekday == 0:
        return 'lunedi'
    if weekday == 3:
        return 'giovedi'
    raise SystemExit('Oggi non è né lunedì né giovedì. Usa FORCE_SLOT per test manuali.')


def compact_problem(problem):
    return {
        'id': problem['id'],
        'topic': problem['topic'],
        'difficulty': problem['difficulty'],
        'title': problem['title'],
        'body': problem['body']
    }


def choose_problem(problems, state, class_code, slot):
    published_for_slot = state.setdefault('published', {}).setdefault(class_code, {}).setdefault(slot, [])
    recent_ids = state.setdefault('recent_ids', [])
    recent_limit = int(state.get('recent_limit', 16))

    candidates = [
        p for p in problems
        if p.get('active', True)
        and p['class_code'] == class_code
        and p.get('preferred_slot', 'any') in (slot, 'any')
        and p['id'] not in recent_ids
        and p['id'] not in published_for_slot
    ]

    if not candidates:
        candidates = [
            p for p in problems
            if p.get('active', True)
            and p['class_code'] == class_code
            and p.get('preferred_slot', 'any') in (slot, 'any')
            and p['id'] not in published_for_slot
        ]

    if not candidates:
        candidates = [
            p for p in problems
            if p.get('active', True)
            and p['class_code'] == class_code
            and p.get('preferred_slot', 'any') in (slot, 'any')
        ]

    if not candidates:
        raise RuntimeError(f'Nessun problema disponibile per {class_code} / {slot}')

    # Prefer less published overall, then random among best
    counts = {}
    for p in problems:
        counts[p['id']] = 0
    for cls, slot_map in state.get('published', {}).items():
        for sl, ids in slot_map.items():
            for pid in ids:
                counts[pid] = counts.get(pid, 0) + 1

    min_count = min(counts.get(p['id'], 0) for p in candidates)
    best = [p for p in candidates if counts.get(p['id'], 0) == min_count]
    chosen = random.choice(best)

    published_for_slot.append(chosen['id'])
    recent_ids.append(chosen['id'])
    if len(recent_ids) > recent_limit:
        del recent_ids[:-recent_limit]

    return chosen


def main():
    random.seed()

    problems = load_json(PROBLEMS_FILE)
    current = load_json(CURRENT_FILE)
    state = load_json(STATE_FILE)

    slot = os.environ.get('FORCE_SLOT', '').strip().lower() or detect_slot()
    if slot not in SLOTS:
        raise SystemExit(f'Slot non valido: {slot}')

    for class_code in CLASS_CODES:
        problem = choose_problem(problems, state, class_code, slot)
        current.setdefault(class_code, {})[slot] = compact_problem(problem)

    current['updated_at'] = utc_now_iso()

    save_json(CURRENT_FILE, current)
    save_json(STATE_FILE, state)

    print(f'Aggiornamento completato per slot: {slot}')


if __name__ == '__main__':
    main()
