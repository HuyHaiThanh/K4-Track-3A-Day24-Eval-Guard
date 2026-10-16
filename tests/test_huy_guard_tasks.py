"""Independent regression coverage for Huy's Tasks 9a/10/12."""
import asyncio
from copy import deepcopy
from unittest.mock import AsyncMock, Mock
import pytest
from src import phase_c_guard as phase

pytestmark = pytest.mark.student


def test_expected_and_category_do_not_control_actual_decision(monkeypatch):
    source = [{"id": 1, "category": "clean", "input": "pii", "expected": "allowed"},
              {"id": 2, "category": "attack", "input": "ordinary", "expected": "blocked"}]
    before = deepcopy(source)
    monkeypatch.setattr(phase, "pii_scan", lambda text, *args: {"has_pii": text == "pii"})
    rail = AsyncMock(return_value={"allowed": True})
    monkeypatch.setattr(phase, "check_input_rail", rail)
    rows = phase.run_adversarial_suite(source, rails=object(), analyzer=object(), anonymizer=object())
    assert [r["actual"] for r in rows] == ["blocked", "allowed"]
    assert [r["passed"] for r in rows] == [False, False]
    assert source == before
    rail.assert_awaited_once()


def test_latency_does_not_short_circuit_pii_or_count_warmup(monkeypatch):
    pii = Mock(return_value={"has_pii": True})
    rail = AsyncMock(return_value={"allowed": False})
    monkeypatch.setattr(phase, "pii_scan", pii)
    monkeypatch.setattr(phase, "check_input_rail", rail)
    monkeypatch.setattr(phase.time, "perf_counter", Mock(side_effect=[i / 1000 for i in range(60)]))
    result = phase.measure_p95_latency(["a", "b"], n_runs=20,
                                      rails=object(), analyzer=object(), anonymizer=object())
    assert pii.call_count == rail.await_count == 22
    assert len(result["samples"]) == 20 and result["warmup_runs"] == 2
    assert result["input_guard_ms"]["p95"] == pytest.approx(2)
    assert all(r["input_guard_ms"] == r["presidio_ms"] + r["nemo_input_ms"] for r in result["samples"])


@pytest.mark.parametrize("runs", [0, -1, True, 1.5])
def test_invalid_sample_counts_fail_before_engine_setup(monkeypatch, runs):
    setup = Mock(side_effect=AssertionError("Must validate before setup"))
    monkeypatch.setattr(phase, "setup_presidio", setup)
    with pytest.raises(ValueError):
        phase.measure_p95_latency(["clean"], n_runs=runs)
    setup.assert_not_called()


def test_sync_runner_rejects_active_loop_without_creating_coroutine():
    async def caller():
        with pytest.raises(RuntimeError, match="active event loop"):
            phase.run_adversarial_suite([])
        with pytest.raises(RuntimeError, match="active event loop"):
            phase.measure_p95_latency(["clean"])
    asyncio.run(caller())


def test_empty_suite_needs_no_engines():
    assert phase.run_adversarial_suite([]) == []


def test_unrelated_english_ner_does_not_block_clean_vietnamese_policy():
    from types import SimpleNamespace
    analyzer = SimpleNamespace(analyze=Mock(return_value=[
        SimpleNamespace(entity_type="PERSON", start=0, end=4, score=.85),
        SimpleNamespace(entity_type="DATE_TIME", start=5, end=9, score=.85),
        SimpleNamespace(entity_type="US_DRIVER_LICENSE", start=5, end=9, score=.01)]))
    anonymizer = Mock()
    assert phase.pii_scan("Phép 2024", analyzer, anonymizer) == {
        "has_pii": False, "entities": [], "anonymized": "Phép 2024"}
    anonymizer.anonymize.assert_not_called()
