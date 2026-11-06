"""Deterministic unit tests for the Task 2 planner contract.

These tests intentionally do not launch Chrome or call Gemini. Browser/model
integration checks are documented as manual smoke tests in the README.
"""
import pytest

from agent import validate_plan


def valid_plan():
    return {
        "test_understanding": "Check that the dashboard is displayed.",
        "steps": [
            {"action": "click", "target": "Sign in"},
            {"action": "verify_text", "target": "Dashboard"},
        ],
        "success_condition": "Dashboard",
    }


def test_valid_plan_is_accepted():
    validate_plan(valid_plan())


def test_empty_plan_is_rejected():
    with pytest.raises(ValueError, match="non-empty list"):
        validate_plan({"steps": [], "success_condition": "Done"})


def test_plan_without_assertion_is_rejected():
    plan = valid_plan()
    plan["steps"] = [{"action": "click", "target": "Submit"}]
    with pytest.raises(ValueError, match="verify_text or verify_element"):
        validate_plan(plan)


def test_missing_target_is_rejected():
    plan = valid_plan()
    plan["steps"][0]["target"] = " "
    with pytest.raises(ValueError, match="non-empty 'target'"):
        validate_plan(plan)


def test_missing_final_success_condition_is_rejected():
    plan = valid_plan()
    del plan["success_condition"]
    with pytest.raises(ValueError, match="success_condition"):
        validate_plan(plan)


@pytest.mark.parametrize("action", ["fill", "select"])
def test_value_required_for_value_actions(action):
    plan = valid_plan()
    plan["steps"] = [{"action": action, "target": "Country"},
                     {"action": "verify_text", "target": "Saved"}]
    with pytest.raises(ValueError, match="requires a 'value'"):
        validate_plan(plan)


def test_goto_requires_absolute_http_url():
    plan = valid_plan()
    plan["steps"].insert(0, {"action": "goto", "url": "/login"})
    with pytest.raises(ValueError, match="absolute http/https URL"):
        validate_plan(plan)


def test_unknown_action_is_rejected():
    plan = valid_plan()
    plan["steps"][0]["action"] = "execute_shell"
    with pytest.raises(ValueError, match="Invalid action"):
        validate_plan(plan)
