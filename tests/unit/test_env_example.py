"""Guard the .env.example template against drifting from the setup docs."""

from pathlib import Path

ENV_EXAMPLE = Path(__file__).resolve().parents[2] / ".env.example"


def _template_keys() -> set[str]:
    keys = set()
    for line in ENV_EXAMPLE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0])
    return keys


def test_env_example_has_openrouter_api_key():
    """README.md and docs/SETUP.md tell users to set OPENROUTER_API_KEY in .env."""
    assert "OPENROUTER_API_KEY" in _template_keys()
