"""Read-only pre-class check: environment, Qdrant, and source-grounded answers."""
from __future__ import annotations

import importlib
from importlib.metadata import version
import json
import hashlib
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import (ANSWERS_PATH, TEST_SET_PATH, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME,
                    DATA_DIR, EMBEDDING_MODEL, MODEL_CPU_THREADS, MODEL_BATCH_SIZE, RERANK_MAX_LENGTH)
from src.report_contracts import validate_answers
from src.m1_chunking import load_documents


def check_preclass():
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError("Lab requires Python 3.11")
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    # On this Windows runtime, initialize torch DLLs before NLP libraries.
    importlib.import_module("torch")
    for name in ("ragas", "nemoguardrails", "presidio_analyzer", "presidio_anonymizer",
                 "spacy", "sentence_transformers", "qdrant_client"):
        importlib.import_module(name)
    import spacy
    spacy.load("en_core_web_lg")
    from qdrant_client import QdrantClient
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        points = client.get_collection(COLLECTION_NAME).points_count
        enrichment_statuses = {}
        offset = None
        while True:
            records, offset = client.scroll(COLLECTION_NAME, limit=256, offset=offset,
                                             with_payload=True, with_vectors=False)
            for record in records:
                status = record.payload.get("enrichment_status", "raw")
                enrichment_statuses[status] = enrichment_statuses.get(status, 0) + 1
            if offset is None:
                break
        if not points:
            raise RuntimeError("Qdrant collection has no indexed chunks")
    finally:
        client.close()
    with open(TEST_SET_PATH, encoding="utf-8") as handle:
        questions = json.load(handle)
    with open(ANSWERS_PATH, encoding="utf-8") as handle:
        answers = json.load(handle)
    validate_answers(answers, questions)
    documents = load_documents()
    # Exact substring verification: synthetic enrichment cannot become context evidence.
    for row in answers:
        if not row["contexts"]:
            raise ValueError(f"Question {row['id']} has no retrieved context")
        for context in row["contexts"]:
            if not any(context in doc["text"] for doc in documents):
                raise ValueError(f"Question {row['id']} has context outside the original corpus")
    distributions = {name: sum(r["distribution"] == name for r in answers)
                     for name in ("factual", "multi_hop", "adversarial")}
    if list(distributions.values()) != [20, 20, 10]:
        raise ValueError("Expected distribution counts 20/20/10")
    return {
        "answers_sha256": hashlib.sha256(Path(ANSWERS_PATH).read_bytes()).hexdigest(),
        "test_set_sha256": hashlib.sha256(Path(TEST_SET_PATH).read_bytes()).hexdigest(),
        "python": platform.python_version(), "os": platform.platform(),
        "packages": {name: version(name) for name in (
            "ragas", "nemoguardrails", "qdrant-client", "sentence-transformers",
            "openai", "spacy", "numpy", "pyarrow", "torch", "transformers")},
        "spacy_model": "en_core_web_lg",
        "qdrant_collection": COLLECTION_NAME, "indexed_points": points,
        "enrichment_statuses_in_index": enrichment_statuses,
        "loaded_documents": len(documents), "answers": len(answers),
        "corpus_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(Path(DATA_DIR).iterdir()) if path.is_file()},
        "local_models": {"embedding": EMBEDDING_MODEL, "reranker": "BAAI/bge-reranker-v2-m3"},
        "inference_settings": {"cpu_threads": MODEL_CPU_THREADS,
                               "batch_size": MODEL_BATCH_SIZE, "reranker_max_length": RERANK_MAX_LENGTH},
        "distributions": distributions, "schema_and_source_validation": "passed",
        "all_contexts_are_original_corpus_substrings": True,
        "context_count_histogram": {str(n): sum(len(r["contexts"]) == n for r in answers)
                                    for n in sorted({len(r["contexts"]) for r in answers})},
        "generation_modes": {mode: sum(r["generation_mode"] == mode for r in answers)
                             for mode in ("llm", "extractive_fallback")},
        "generation_models": sorted({r["generation_model"] for r in answers
                                      if r["generation_model"] is not None}),
        "limits": ["Scanned PDFs without a text layer require OCR and are skipped.",
                   "Import checks do not prove live NeMo rails or RAGAS evaluation."],
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(check_preclass(), ensure_ascii=False, indent=2))
