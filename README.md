<!-- Brand Tokens: Dark Teal #0A1A1D | Gold #FFD700 | Royal Purple #6A1B9A | Fonts: Poppins & Lora -->

# Divinari Language Resources

**Where faith meets fluency.**  
*Learn languages. Discover heritage. Grow in faith.*

`divinari-language-resources` is an open, community-supported repository of linguistic metadata, vocabulary submissions, pronunciation guides, grammar notes, and writing-system documentation curated for heritage preservation and open language tooling.

> **Commercial & Open-Ecosystem Notice:** **Divinari** (`https://divinari.app`) is a commercially operated, proprietary language-learning platform. The Divinari mobile/web codebase, Firebase backend, encrypted production bundles, commercial Heritage Packs, and AI tutoring prompts remain private and proprietary. Merged community resources here remain open under **CC BY 4.0** and never auto-deploy to production apps.

---

## Language Track Availability

> **Important Note:** Presence of a language directory under `languages/` (`tl/`, `ceb/`, `ilo/`, `hil/`, `es/`, `de/`, `fr/`, `en/`) provides a standardized contribution structure and metadata file—it does **not** mean complete verified datasets already exist for that language. Initial `languages/*/metadata.json` records currently carry `status: "scaffold"` (`verified_entry_count: 0`) pending native-speaker provenance verification and curation.

---

## Structure

- `languages/` — Per-language metadata scaffolds and reviewed open lexicon/example datasets
- `writing-systems/` — Open stroke-order and Unicode coordinate specifications for 11 core world writing systems (`CC BY 4.0`)
- `schemas/` — Pinned copies of Draft 2020-12 JSON Schemas from [`Divinari/divinari-developer-resources`](https://github.com/Divinari/divinari-developer-resources) (`Apache 2.0`)
- `regional-variants/` — Documentation honoring regional varieties and distinct languages
- `pronunciation/` — IPA & syllabic notation guides *(synthetic TTS prohibited; audio uploads blocked until Phase 5 Voice Release)*
- `grammar/` — Open morphological & syntactic references
- `attribution/` — [Contributors](./attribution/CONTRIBUTORS.md), [Third-Party Sources](./attribution/THIRD_PARTY_SOURCES.md), and draft [Voice Release Template](./attribution/VOICE_RELEASE_TEMPLATE.md)
- `validation/` — Automated 7-layer CI validation scripts and tests (`Apache 2.0`)

---

## Licensing, Contributions & Security

- Linguistic datasets and documentation: **CC BY 4.0** ([LICENSE](./LICENSE)); `schemas/` and `validation/`: **Apache License 2.0**.
- Trademarks and Hummingbird brand artwork remain **All Rights Reserved** ([TRADEMARK.md](./TRADEMARK.md)).
- Contributions require **DCO 1.1** (`Signed-off-by:`), human verification, and explicit provenance ([CONTRIBUTING.md](./CONTRIBUTING.md)).
- Vulnerability & provenance concerns: [SECURITY.md](./SECURITY.md).
