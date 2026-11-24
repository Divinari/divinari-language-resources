# Contributing to `divinari-language-resources`

We welcome native speakers, linguists, educators, and heritage speakers!

## Mandatory Rules

1. **Human Authorship & Verification Required:** Unreviewed bulk AI/LLM output dumps are rejected. Every linguistic entry must be authored or verified by a qualified human contributor (`native-reviewed` or `linguist-reviewed`).
2. **Clean Licensing & Explicit Provenance:** Declare `license` (`CC-BY-4.0` or `CC0-1.0`), `origin_type`, and `source_citation` in every submission. Never copy modern commercial dictionaries, copyrighted Bible editions, or consumer text-to-speech audio.
3. **Zero Synthetic Fillers:** Automated CI blocks numbered suffixes, placeholder phrases, duplicate keys, and mismatched example-sentence token offsets.
4. **DCO 1.1 Sign-Off (`git commit -s`):** Every commit must include `Signed-off-by: Your Name <you@example.org>`.
5. **No Auto-Deployment:** Merging a PR publishes to this open `CC BY 4.0` dataset; downstream integration into Divinari's private app occurs separately after manual maintainer audit and attribution updates.

## Run Checks Locally Before Opening a PR

```bash
python3 -m pip install -r validation/requirements.txt
python3 validation/run_checks.py --check all --schemas-dir schemas/
pytest -q validation/tests/
```
