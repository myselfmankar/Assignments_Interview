import pytest
from agent import validate_plan, run_test

def test_plan_validation_empty():
    """Ensure empty or invalid action plans are rejected."""
    with pytest.raises(ValueError, match="non-empty list"):
        validate_plan({"steps": []})

def test_plan_validation_no_assertions():
    """Ensure plans without any verification step are rejected."""
    plan = {
        "steps": [
            {"action": "click", "target": "Submit"}
        ]
    }
    with pytest.raises(ValueError, match="lacks any verification"):
        validate_plan(plan)

def test_plan_validation_missing_target():
    """Ensure action steps without target are rejected."""
    plan = {
        "steps": [
            {"action": "click", "target": ""},
            {"action": "verify_text", "target": "Done"}
        ]
    }
    with pytest.raises(ValueError, match="requires a 'target'"):
        validate_plan(plan)

def test_negative_assertion_fails_correctly():
    """Verify that an impossible assertion results in FAIL (never a false PASS)."""
    success = run_test(
        test_case="Verify that the text 'nonexistent_impossible_token_9999' is rendered on the page",
        start_url="https://example.com",
        headed=False
    )
    assert success is False, "Agent should fail when asserting nonexistent content"

def test_positive_arbitrary_site_passes():
    """Verify site independence on an arbitrary website."""
    success = run_test(
        test_case="Verify that the More information link is present on the page",
        start_url="https://example.com",
        headed=False
    )
    assert success is True, "Agent should pass on valid assertion on example.com"
