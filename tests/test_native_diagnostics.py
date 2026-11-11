"""Actual failure-summary privacy/bounds tests; no process, service or application result is mocked into a pass. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_native_failure_summary_keeps_only_authored_stage_and_counts — line 14
# variable: value — line 16
# definition: test_native_failure_summary_discards_private_values_and_invalid_bounds — line 42
# variable: n — line 52
# definition: test_comparative_namespace_summary_never_exports_raw_control_data — line 58
# variable: control — line 86
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


def test_comparative_namespace_summary_never_exports_raw_control_data():
    """Only complete fixed-class observations escape; malformed nested data cannot masquerade as successful evidence."""
    from scripts.test_native_app import namespace_summary

    assert namespace_summary(
        {
            "direct_php_namespace_control": {
                "passed": True,
                "http_cases": 24,
                "scope": "PRIVATE-INERT",
            }
        }
    ) == {
        "direct_extraction_control_passed": True,
        "direct_extraction_control_http_cases": 24,
    }
    assert namespace_summary(
        {
            "direct_php_namespace_control": {
                "passed": False,
                "category": "owned_php_driver_module_missing",
                "raw": "PRIVATE-INERT",
            }
        }
    ) == {
        "direct_extraction_control_passed": False,
        "direct_extraction_control_category": "owned_php_driver_module_missing",
    }
    for control in (
        None,
        [],
        {"passed": 1, "http_cases": 24},
        {"passed": True, "http_cases": True},
        {"passed": True, "http_cases": 23},
        {"passed": False, "category": ["PRIVATE-INERT"]},
        {"passed": False, "category": "PRIVATE-INERT"},
    ):
        assert namespace_summary({"direct_php_namespace_control": control}) == {}
