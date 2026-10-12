"""Offline regressions for the pre-class pipeline integration fixes."""
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.support


def test_hierarchical_chunks_preserve_text_and_source():
    from src.m1_chunking import chunk_hierarchical
    text = "Chính sách cũ.\n\n" + "Nhân viên được nghỉ phép. " * 20
    parents, children = chunk_hierarchical(text, parent_size=100, child_size=40,
                                           metadata={"source": "policy_v2023.md"})
    assert "".join(p.text for p in parents) == text
    assert "".join(c.text for c in children) == text
    assert all(len(c.text) <= 40 for c in children)
    assert all(c.metadata["source"] == "policy_v2023.md" for c in children)
    assert all(c.parent_id in {p.metadata["parent_id"] for p in parents} for c in children)


def test_dense_search_uses_pinned_qdrant_search_api():
    from src.m2_search import DenseSearch
    search = DenseSearch.__new__(DenseSearch)
    search.client = Mock()
    search.client.collection_exists.return_value = True
    search.client.get_collection.return_value = SimpleNamespace(points_count=1)
    search.client.search.return_value = [SimpleNamespace(
        payload={"text": "policy", "source": "policy.md", "parent_id": "p"}, score=.8)]
    search._encoder = SimpleNamespace(encode=lambda q: SimpleNamespace(tolist=lambda: [1., 0.]))
    rows = search.search("nghỉ phép", top_k=3)
    search.client.search.assert_called_once_with(collection_name="lab24_production",
        query_vector=[1., 0.], limit=3, with_payload=True)
    assert rows[0].metadata == {"source": "policy.md", "parent_id": "p"}
    assert rows[0].text == "policy"


def test_enrichment_preserves_order_and_authoritative_metadata(monkeypatch):
    from src import m5_enrichment as m5
    monkeypatch.setattr(m5, "OPENAI_API_KEY", "")
    chunks = [{"text": text, "metadata": {"source": source, "parent_id": str(i)}}
              for i, (text, source) in enumerate([("Chính sách 2023.", "old.md"),
                                                 ("Chính sách 2024.", "new.md")])]
    enriched = m5.enrich_chunks(chunks)
    assert [e.original_text for e in enriched] == [c["text"] for c in chunks]
    for original, result in zip(chunks, enriched):
        assert original["text"] in result.enriched_text
        assert result.auto_metadata["source"] == original["metadata"]["source"]
        assert result.auto_metadata["parent_id"] == original["metadata"]["parent_id"]
        assert result.auto_metadata["enrichment_status"] == "fallback"


def test_ragas_reports_models_passed_to_evaluation(monkeypatch):
    from src import m4_eval as m4
    monkeypatch.setattr(m4, "OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("RAGAS_MODEL", "evaluator-llm")
    monkeypatch.setenv("RAGAS_EMBEDDING_MODEL", "evaluator-embedding")
    metric_row = dict.fromkeys(m4.METRIC_NAMES, .7)
    frame = SimpleNamespace(iterrows=lambda: iter([(0, metric_row)]))
    class Frame:
        def __len__(self): return 1
        def iterrows(self): return frame.iterrows()
    evaluate = Mock(return_value=SimpleNamespace(to_pandas=lambda: Frame()))
    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(
        Dataset=SimpleNamespace(from_dict=lambda values: values)))
    monkeypatch.setitem(sys.modules, "ragas", SimpleNamespace(evaluate=evaluate))
    monkeypatch.setitem(sys.modules, "ragas.metrics", SimpleNamespace(**{
        name: name for name in m4.METRIC_NAMES}))
    monkeypatch.setitem(sys.modules, "ragas.run_config", SimpleNamespace(RunConfig=lambda **kw: kw))
    monkeypatch.setitem(sys.modules, "langchain_openai", SimpleNamespace(
        ChatOpenAI=lambda **kw: kw, OpenAIEmbeddings=lambda **kw: kw))
    result = m4.evaluate_ragas(["Q"], ["A"], [["C"]], ["GT"])
    assert result["metadata"]["evaluator_models"] == ["evaluator-llm", "evaluator-embedding"]
    assert evaluate.call_args.kwargs["llm"]["model"] == "evaluator-llm"
    assert evaluate.call_args.kwargs["embeddings"]["model"] == "evaluator-embedding"
    assert result["per_question"][0].faithfulness == .7
    metric_row["faithfulness"] = float("nan")
    with pytest.raises(RuntimeError):
        m4.evaluate_ragas(["Q"], ["A"], [["C"]], ["GT"])


def test_empty_generation_is_explicit_extractive_fallback():
    from scripts.setup_answers import run_query
    search = SimpleNamespace(search=lambda q: [SimpleNamespace(text="retrieved context", score=.5,
                                                               metadata={"source": "policy"})])
    reranker = SimpleNamespace(rerank=lambda *args, **kw: [])
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=""))])
    assert run_query("Q", search, reranker, 3, client) == (
        "retrieved context", ["retrieved context"], "extractive_fallback", None)


def test_generation_context_uses_source_parent_not_generated_enrichment():
    from scripts.setup_answers import run_query
    metadata = {"parent_text": "Original policy including version and conditions.",
                "original_text": "Small original child."}
    hit = SimpleNamespace(text="Generated summary and hypothetical questions", score=.8,
                          metadata=metadata)
    search = SimpleNamespace(search=lambda q: [hit])
    reranker = SimpleNamespace(rerank=lambda *args, **kw: [hit, hit])
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(model="provider-model",
        choices=[SimpleNamespace(message=SimpleNamespace(content="Generated answer"))])
    answer, contexts, mode, model = run_query("Q", search, reranker, 3, client)
    assert contexts == [metadata["parent_text"]]
    assert "Generated summary" not in client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert (mode, model) == ("llm", "provider-model")


def test_invalid_batch_does_not_replace_existing_answers(tmp_path, monkeypatch):
    from scripts import setup_answers as setup
    import config
    destination = tmp_path / "answers_50q.json"
    destination.write_text("previous successful batch", encoding="utf-8")
    monkeypatch.setattr(setup, "ANSWERS_PATH", str(destination))
    monkeypatch.setattr(setup, "check_day18_files", lambda: True)
    monkeypatch.setattr(setup, "build_pipeline", lambda: (None, None, 3))
    monkeypatch.setattr(setup, "run_query", lambda *args: (123, ["context"], "extractive_fallback", None))
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    with pytest.raises(ValueError):
        setup.main(["--live"])
    assert destination.read_text(encoding="utf-8") == "previous successful batch"


def test_enrichment_order_changes_are_rejected_before_indexing(monkeypatch):
    from scripts import setup_answers as setup
    children = [SimpleNamespace(text=t, metadata={"source": "policy"}, parent_id="p")
                for t in ("first", "second")]
    monkeypatch.setitem(sys.modules, "src.m1_chunking", SimpleNamespace(
        load_documents=lambda: [{"text": "document", "metadata": {"source": "policy"}}],
        chunk_hierarchical=lambda *args, **kw: ([], children)))
    monkeypatch.setitem(sys.modules, "src.m2_search", SimpleNamespace(
        HybridSearch=Mock(side_effect=AssertionError("Must reject before indexing"))))
    monkeypatch.setitem(sys.modules, "src.m3_rerank", SimpleNamespace(CrossEncoderReranker=Mock()))
    monkeypatch.setitem(sys.modules, "src.m5_enrichment", SimpleNamespace(
        enrich_chunks=lambda chunks: [SimpleNamespace(original_text=t, enriched_text=t, auto_metadata={})
                                     for t in ("second", "first")]))
    with pytest.raises(ValueError, match="changed chunk order"):
        setup.build_pipeline()


def test_generation_only_reuses_validated_contexts_without_retrieval(tmp_path, monkeypatch):
    import json
    import config
    import openai
    from scripts import setup_answers as setup
    from src import m1_chunking
    questions = json.loads(open(setup.TEST_SET_PATH, encoding="utf-8").read())
    saved = [{**q, "answer": "Previous extractive answer", "contexts": ["Original policy."],
              "generation_mode": "extractive_fallback", "generation_model": None}
             for q in questions]
    destination = tmp_path / "answers_50q.json"
    destination.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(setup, "ANSWERS_PATH", str(destination))
    monkeypatch.setattr(setup, "check_day18_files", lambda: True)
    monkeypatch.setattr(setup, "build_pipeline", Mock(side_effect=AssertionError("Must reuse retrieval")))
    monkeypatch.setattr(m1_chunking, "load_documents", lambda: [{"text": "Original policy."}])
    monkeypatch.setattr(config, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai, "OpenAI", Mock(return_value=object()))
    generate = Mock(side_effect=lambda q, contexts, client: (
        "Measured mock in unit test only", contexts, "llm", "test-generation-model"))
    monkeypatch.setattr(setup, "generate_answer", generate)
    setup.main(["--live", "--generation-only"])
    actual = json.loads(destination.read_text(encoding="utf-8"))
    assert generate.call_count == 50
    assert [r["contexts"] for r in actual] == [r["contexts"] for r in saved]
    assert [r["ground_truth"] for r in actual] == [q["ground_truth"] for q in questions]
    assert all(r["generation_mode"] == "llm" for r in actual)
    assert all(len(call.args) == 3 and call.args[1] == ["Original policy."]
               for call in generate.call_args_list)
