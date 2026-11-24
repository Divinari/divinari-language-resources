# SPDX-License-Identifier: Apache-2.0
"""Self-tests for divinari-language-resources validation gate."""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "validation"))

import run_checks  # noqa: E402


def test_repo_scaffolds_pass_all_seven_layers() -> None:
    errs = run_checks.run_all_checks("all", ROOT, ROOT / "schemas")
    assert errs == [], f"Unexpected repo validation errors: {errs}"


def test_negative_in_memory_payload_rejections() -> None:
    bad_synth = {
        "entries": [{"term": "kalakal-pampinansiyal-131", "normalized_term": "kalakal-pampinansiyal-131"}]
    }
    assert run_checks.check_payload_rules(bad_synth, "mem", "anti-synthetic")

    bad_lic = {"license": "CC-BY-SA-4.0", "source_citation": "edge-tts synthesis"}
    assert len(run_checks.check_payload_rules(bad_lic, "mem", "provenance-and-license")) >= 2

    bad_span = {
        "sentences": [
            {
                "sentence_text": "Magandang umaga po.",
                "tokens": [{"surface": "umaga", "char_start": 0, "char_end": 5}],
            }
        ]
    }
    assert run_checks.check_payload_rules(bad_span, "mem", "duplicates-and-spans")
