"""Actual failure-summary privacy/bounds tests; no process, service or application result is mocked into a pass. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_native_failure_summary_keeps_only_authored_stage_and_counts — line 12
# variable: value — line 14
# definition: test_native_failure_summary_discards_private_values_and_invalid_bounds — line 40
# variable: n — line 50
# END CODE MAP

from scripts.test_native_app import failure_summary


def test_native_failure_summary_keeps_only_authored_stage_and_counts():
    """A real receipt-shaped failure reveals useful exact assertion location without private contents."""
    value = failure_summary(
        {
            "failure_stage": "<lambda>",
            "failure_step": "workflow-1",
            "failure_type": "AssertionError",
            "failure_function": "oracle",
            "failure_line": 245,
            "steps": ["actual-workflow-1"],
            "bundles": {"1": {"private.json": "private"}},
            "safe_application_status": "Input/output rejected: java_owned_service_exited. Earlier saved analyses were retained.",
            "unexpected_secret": "do-not-output",
        }
    )
    assert value == {
        "native_acceptance": "failed",
        "failure_stage": "<lambda>",
        "failure_step": "workflow-1",
        "failure_type": "AssertionError",
        "failure_function": "oracle",
        "failure_line": 245,
        "completed_steps": 1,
        "saved_bundles": 1,
        "application_category": "java_owned_service_exited",
    }


def test_native_failure_summary_discards_private_values_and_invalid_bounds():
    """Arbitrary status/paths, overlong fields, boolean line numbers and malformed collections stay absent."""
    assert failure_summary(
        {
            "failure_stage": "C:/private/account",
            "failure_step": "x" * 81,
            "failure_type": None,
            "failure_function": "secret value",
            "failure_line": True,
            "steps": ["x"] * 41,
            "bundles": {str(n): "secret" for n in range(21)},
            "safe_application_status": "private user input and provider key",
        }
    ) == {"native_acceptance": "failed"}
