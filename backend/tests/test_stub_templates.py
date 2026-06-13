import pytest

from src.schema import ModuleConfig
from src.stub_templates import pick_template


@pytest.mark.parametrize(
    "prompt,expected_keyword",
    [
        ("track my workouts at the gym", "Workout"),  # plural must still route
        ("workout", "Workout"),
        ("a calorie tracker for my diet", "Calorie"),
        ("budget for a trip to Japan", "Budget"),
        ("a to-do list for chores", "To-Do"),
        ("my reading list of books", "Reading"),
        ("daily habit streak", "Habit"),
        ("a mood journal", "Mood"),
    ],
)
def test_pick_template_routes_by_intent(prompt, expected_keyword):
    config = pick_template(prompt)
    assert expected_keyword.lower() in config["title"].lower()
    # Every template must validate as a real ModuleConfig.
    ModuleConfig.model_validate(config)


def test_pick_template_falls_back_to_generic():
    config = pick_template("xyzzy quux frobnicate")
    parsed = ModuleConfig.model_validate(config)
    assert parsed.components  # generic still produces a usable module


def test_generic_title_strips_filler_and_does_not_double_tracker():
    config = pick_template("I want to create a tracker for my plants")
    title = config["title"]
    assert "tracker" not in title.lower()  # filler stripped, no "Tracker Tracker"
    assert "Plants" in title


def test_every_template_validates():
    prompts = [
        "workout", "calorie", "budget", "todo", "reading", "habit", "mood",
        "random thing",
    ]
    for p in prompts:
        ModuleConfig.model_validate(pick_template(p))
