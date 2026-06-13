"""Intent-aware canned ModuleConfigs for dev when no Gemini key is set.

This is the offline fallback that lets the full pipeline be exercised without a
real API key. It keyword-routes a prompt to a sensible, differentiated module so
that "track my workouts" and "trip budget" produce genuinely different tools —
not the same canned card. A real Gemini key bypasses all of this (see llm.py).
"""
from __future__ import annotations

import re

# Each template is a function returning the components/layout for that domain.
# Keep them small but real: enough to feel like a working tool.


def _workout() -> dict:
    return {
        "title": "Workout Log",
        "components": [
            {"id": "exercise", "type": "text_input", "label": "Exercise", "placeholder": "e.g. Bench press"},
            {"id": "sets", "type": "number_input", "label": "Sets", "min": 0, "step": 1},
            {"id": "reps", "type": "number_input", "label": "Reps", "min": 0, "step": 1},
            {"id": "weight", "type": "slider", "label": "Weight", "min": 0, "max": 315, "step": 5, "unit": "lb"},
            {"id": "done_today", "type": "checkbox", "label": "Done today"},
            {"id": "weekly", "type": "progress_bar", "label": "Weekly sessions", "max": 5, "bound_to": "sets"},
        ],
        "summary_component_id": "weekly",
    }


def _calorie() -> dict:
    return {
        "title": "Calorie Tracker",
        "components": [
            {"id": "meals", "type": "list", "label": "Meals today", "item_label": "Meal", "placeholder": "e.g. Oatmeal — 320 cal"},
            {"id": "calories", "type": "number_input", "label": "Calories so far", "min": 0, "step": 10, "unit": "cal"},
            {"id": "goal_progress", "type": "progress_bar", "label": "Daily goal (2000)", "max": 2000, "bound_to": "calories"},
            {"id": "water_glasses", "type": "number_input", "label": "Water", "min": 0, "step": 1, "unit": "glasses"},
        ],
        "summary_component_id": "goal_progress",
    }


def _budget() -> dict:
    return {
        "title": "Budget",
        "components": [
            {"id": "destination", "type": "text_input", "label": "What for", "placeholder": "e.g. Trip to Japan"},
            {"id": "total_budget", "type": "slider", "label": "Total budget", "min": 0, "max": 5000, "step": 50, "unit": "$"},
            {"id": "expenses", "type": "list", "label": "Expenses", "item_label": "Expense", "placeholder": "e.g. Flights — $650"},
            {"id": "spent", "type": "number_input", "label": "Spent so far", "min": 0, "step": 10, "unit": "$"},
            {"id": "spent_progress", "type": "progress_bar", "label": "Budget used", "max": 5000, "bound_to": "spent"},
        ],
        "summary_component_id": "spent_progress",
    }


def _todo() -> dict:
    return {
        "title": "To-Do List",
        "components": [
            {"id": "tasks", "type": "list", "label": "Tasks", "item_label": "Task", "placeholder": "Add a task…"},
            {"id": "done_count", "type": "number_input", "label": "Completed today", "min": 0, "step": 1},
            {"id": "progress", "type": "progress_bar", "label": "Daily target", "max": 10, "bound_to": "done_count"},
        ],
        "summary_component_id": "progress",
    }


def _reading() -> dict:
    return {
        "title": "Reading List",
        "components": [
            {"id": "books", "type": "list", "label": "Books", "item_label": "Book", "placeholder": "e.g. Dune — Frank Herbert"},
            {"id": "current", "type": "text_input", "label": "Currently reading", "placeholder": "Title"},
            {"id": "pages_read", "type": "number_input", "label": "Pages read", "min": 0, "step": 1},
            {"id": "book_progress", "type": "progress_bar", "label": "Toward book (350 pp)", "max": 350, "bound_to": "pages_read"},
        ],
        "summary_component_id": "book_progress",
    }


def _habit() -> dict:
    return {
        "title": "Habit Tracker",
        "components": [
            {"id": "habit", "type": "text_input", "label": "Habit", "placeholder": "e.g. Meditate"},
            {"id": "done_today", "type": "checkbox", "label": "Done today"},
            {"id": "streak", "type": "number_input", "label": "Current streak", "min": 0, "step": 1, "unit": "days"},
            {"id": "month", "type": "progress_bar", "label": "30-day goal", "max": 30, "bound_to": "streak"},
        ],
        "summary_component_id": "month",
    }


def _mood() -> dict:
    return {
        "title": "Mood Journal",
        "components": [
            {"id": "entry", "type": "text_input", "label": "Today", "placeholder": "How was your day?"},
            {"id": "mood", "type": "slider", "label": "Mood", "min": 1, "max": 10, "step": 1},
            {"id": "tags", "type": "list", "label": "Tags", "item_label": "Tag", "placeholder": "e.g. calm"},
            {"id": "gratitude", "type": "list", "label": "Grateful for", "item_label": "Item"},
        ],
        "summary_component_id": "mood",
    }


def _generic(prompt: str) -> dict:
    title = _clean_title(prompt)
    return {
        "title": title,
        "components": [
            {"id": "name", "type": "text_input", "label": "Name", "placeholder": title},
            {"id": "items", "type": "list", "label": "Items", "item_label": "Item", "placeholder": "Add an item…"},
            {"id": "count", "type": "number_input", "label": "Count", "min": 0, "step": 1},
            {"id": "notes", "type": "text_input", "label": "Notes", "placeholder": "Anything to remember"},
        ],
        "summary_component_id": "count",
    }


# Keyword → template. First match wins; order matters for overlaps.
_ROUTES: list[tuple[tuple[str, ...], object]] = [
    (("workout", "exercise", "gym", "lift", "fitness", "run", "training"), _workout),
    (("calorie", "food", "meal", "eat", "nutrition", "diet", "macro"), _calorie),
    (("budget", "expense", "spend", "money", "cost", "saving", "finance"), _budget),
    (("todo", "to-do", "task", "checklist", "chore", "groc"), _todo),
    (("read", "book", "reading", "watchlist", "watch list"), _reading),
    (("habit", "streak", "routine", "daily"), _habit),
    (("mood", "journal", "gratitude", "feeling", "reflect", "diary"), _mood),
]

_FILLER = {
    "a", "an", "the", "my", "to", "for", "of", "i", "want", "need",
    "create", "make", "build", "track", "tracker", "tracking", "something",
    "that", "keeps", "keep", "help", "me", "with",
}


def _clean_title(prompt: str) -> str:
    words = re.findall(r"[A-Za-z0-9']+", prompt)
    kept = [w for w in words if w.lower() not in _FILLER]
    chosen = (kept or words)[:4]
    if not chosen:
        return "Workspace"
    return " ".join(w.capitalize() for w in chosen)


def _matches(keyword: str, text: str) -> bool:
    # Anchor at the START of a word only (not the end), so a keyword matches its
    # plurals/suffixes ("workout" -> "workouts", "read" -> "reading") while a
    # short keyword still can't fire mid-word ("eat" must not match "create").
    return re.search(rf"\b{re.escape(keyword)}", text) is not None


def pick_template(prompt: str) -> dict:
    """Return a full ModuleConfig dict for the given prompt."""
    lower = prompt.lower()
    config = None
    for keywords, builder in _ROUTES:
        if any(_matches(k, lower) for k in keywords):
            config = builder()  # type: ignore[operator]
            break
    if config is None:
        config = _generic(prompt)

    config.setdefault("state", {})
    config.setdefault("layout", {"x": 80, "y": 120, "width": 380, "height": 460})
    return config
