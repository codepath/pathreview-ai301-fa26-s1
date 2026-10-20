"""Tests for Orchestrator resuming from per-tool progress (issue #17)."""

import json
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from agent.orchestrator import Orchestrator

if TYPE_CHECKING:
    from agent.memory.session_store import SessionStore


class FakeSessionStore:
    """In-memory stand-in for SessionStore that survives across Orchestrator instances."""

    def __init__(self):
        self.data = {}

    def get(self, session_id):
        raw = self.data.get(session_id)
        return json.loads(raw) if raw else None

    def set(self, session_id, data, ttl_seconds=3600):
        self.data[session_id] = json.dumps(data)


class FakeTool:
    """Tool stub that counts calls and can be told to die mid-run."""

    def __init__(self, name, calls, die=False):
        self.name = name
        self.calls = calls
        self.die = die

    def execute(self, tool_input):
        self.calls[self.name] = self.calls.get(self.name, 0) + 1
        if self.die:
            raise KeyboardInterrupt  # simulates the process being killed mid-tool
        return SimpleNamespace(data={"tool": self.name})


PROFILE = {
    "files": ["a.py"],
    "readme_content": "# readme",
    "resume_text": "python",
}


def make_orchestrator(tools, store):
    """Build an Orchestrator around the in-memory store."""
    return Orchestrator(tools, cast("SessionStore", store))


def make_tools(calls, die_in=None):
    names = ["tech_detector", "readme_scorer", "skill_extractor", "market_analyzer"]
    return {n: FakeTool(n, calls, die=(n == die_in)) for n in names}


@pytest.mark.unit
class TestOrchestratorResume:
    """Test suite for per-tool persistence and resume."""

    def test_restart_skips_tools_that_finished_before_the_kill(self):
        store = FakeSessionStore()
        calls: dict[str, int] = {}

        with pytest.raises(KeyboardInterrupt):
            make_orchestrator(make_tools(calls, die_in="skill_extractor"), store).run("p1", PROFILE)

        saved = store.get("p1")
        assert saved is not None
        assert saved["tech_detector"] == {"tool": "tech_detector"}
        assert saved["readme_scorer"] == {"tool": "readme_scorer"}
        assert "skill_extractor" not in saved

        calls.clear()
        result = make_orchestrator(make_tools(calls), store).run("p1", PROFILE)

        assert calls == {"skill_extractor": 1, "market_analyzer": 1}
        assert set(result["tool_results"]) == {
            "tech_detector",
            "readme_scorer",
            "skill_extractor",
            "market_analyzer",
        }

    def test_changed_input_reruns_the_tool(self):
        store = FakeSessionStore()
        calls: dict[str, int] = {}
        make_orchestrator(make_tools(calls), store).run("p1", PROFILE)

        calls.clear()
        changed = {**PROFILE, "readme_content": "# a different readme"}
        make_orchestrator(make_tools(calls), store).run("p1", changed)

        assert calls.get("readme_scorer") == 1
        assert "tech_detector" not in calls
