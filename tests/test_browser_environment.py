"""Jason Stys: retain the original complete browser suite on a matching nonroot digest-pinned official image."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 24
# definition: require_environment — line 27
# parameter: source — line 27
# variable: browser — line 29
# variable: version — line 30
# variable: value — line 37
# variable: value — line 49
# definition: test_actual_browser_workflow_retains_matching_image_and_all_original_assertions — line 60
# variable: config — line 63
# variable: name — line 64
# definition: test_browser_recipe_mutants_cannot_remove_real_acceptance — line 84
# parameter: after — line 84
# parameter: before — line 84
# variable: source — line 86
# END CODE MAP

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def require_environment(source: str) -> None:
    """The actual workflow must preserve all real engine/mobile assertions, not just setup success."""
    browser = source.split("  browser:\n", 1)[1].split("  security:\n", 1)[0]
    version = json.loads((ROOT / "package-lock.json").read_text())["packages"][
        "node_modules/playwright"
    ]["dependencies"]["playwright-core"]
    assert (
        f"image: mcr.microsoft.com/playwright:v{version}-noble@sha256:eff16c30e6f3f4af0a03fa4b706120d5e9b0891c344a27d64559aff5900a4a27"
        in browser
    )
    for value in (
        "options: --user 1001",
        "timeout-minutes: 20",
        "node scripts/check_browser_host.mjs chromium firefox webkit",
        "npm run test:e2e",
        "npm run typecheck",
        "npm run build",
        "npm run test:unit",
    ):
        assert value in browser
    assert not any(
        value in browser
        for value in (
            "apt-get",
            "with-deps",
            "install-deps",
            "SKIP_VALIDATE_HOST_REQUIREMENTS",
            "continue-on-error",
            "|| true",
        )
    )


def test_actual_browser_workflow_retains_matching_image_and_all_original_assertions():
    """Match the real locked package, exact source recipe and every existing test project."""
    require_environment((ROOT / ".github/workflows/ci.yml").read_text())
    config = (ROOT / "playwright.config.mjs").read_text()
    for name in ("chromium", "firefox", "webkit", "mobile"):
        assert name in config


@pytest.mark.parametrize(
    "before,after",
    [
        (
            "@sha256:eff16c30e6f3f4af0a03fa4b706120d5e9b0891c344a27d64559aff5900a4a27",
            "",
        ),
        ("--user 1001", "--user 0"),
        ("chromium firefox webkit", "chromium firefox"),
        ("npm run test:e2e", "true"),
        (
            "node scripts/check_browser_host.mjs chromium firefox webkit",
            "node scripts/check_browser_host.mjs chromium firefox webkit || true",
        ),
    ],
)
def test_browser_recipe_mutants_cannot_remove_real_acceptance(before, after):
    """Each independent actual-workflow mutation must fail before it could hide an application fault."""
    source = (ROOT / ".github/workflows/ci.yml").read_text()
    with pytest.raises(AssertionError):
        require_environment(source.replace(before, after))
