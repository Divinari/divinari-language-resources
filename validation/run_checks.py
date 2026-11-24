# SPDX-License-Identifier: Apache-2.0
"""7-layer validation runner for divinari-language-resources."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata
from typing import Any

try:
    from jsonschema import Draft202012Validator  # type: ignore
except ImportError:  # pragma: no cover
    Draft202012Validator = None

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv"}
CONTENT_DIRS = ("languages", "regional-variants", "pronunciation", "grammar", "writing-systems")

DISALLOWED_LICENSE_VALUES = {"CC-BY-SA", "CC-BY-SA-4.0", "ALL RIGHTS RESERVED", "UNKNOWN", "PROPRIETARY"}
FORBIDDEN_CITATION_TERMS = ("edge-tts", "google tts", "lai ", "pbs 1978+", "kwf commercial")
SYNTHETIC_SUFFIX_RE = re.compile(r"(?:[-_]\d+|\(\d+\))$", re.IGNORECASE)
SYNTHETIC_TEXT_PATTERNS = [
    re.compile(r"\(nuance\s+\d+\)", re.IGNORECASE),
    re.compile(r"plays a vital role in", re.IGNORECASE),
    re.compile(r"^Definition in .+ for\b", re.IGNORECASE),
    re.compile(r"^Sample sentence (?:with|containing)\b", re.IGNORECASE),
    re.compile(r"^commercial trade instrument", re.IGNORECASE),
    re.compile(r"^Lexical entry for\b", re.IGNORECASE),
]


def _check_type(value: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_check_type(value, t) for t in expected)
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def _stdlib_validate_schema(data: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    if "type" in schema and not _check_type(data, schema["type"]):
        return [f"{path}: expected {schema['type']}, got {type(data).__name__}"]
    if "const" in schema and data != schema["const"]:
        errors.append(f"{path}: expected {schema['const']!r}, got {data!r}")
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: {data!r} not in {schema['enum']}")
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{path}: len < minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], data):
            errors.append(f"{path}: {data!r} fails pattern {schema['pattern']}")
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: {data} < minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: {data} > maximum {schema['maximum']}")
    if isinstance(data, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in data:
                errors.append(f"{path}: missing required key {req!r}")
        if schema.get("additionalProperties") is False:
            for k in data:
                if k not in props:
                    errors.append(f"{path}: unexpected property {k!r}")
        for k, v in data.items():
            if k in props:
                errors.extend(_stdlib_validate_schema(v, props[k], f"{path}.{k}"))
    if isinstance(data, list):
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: len < minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(data):
                errors.extend(_stdlib_validate_schema(item, schema["items"], f"{path}[{i}]"))
    return errors


def _validate_schema_obj(data: Any, schema: dict[str, Any]) -> list[str]:
    if Draft202012Validator is not None:
        v = Draft202012Validator(schema)
        return [f"{'/'.join(str(p) for p in err.path) or '$'}: {err.message}" for err in v.iter_errors(data)]
    return _stdlib_validate_schema(data, schema)


def _iter_repo_files(repo_root: pathlib.Path) -> list[pathlib.Path]:
    files = []
    for path in sorted(repo_root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts) or path.is_dir():
            continue
        files.append(path)
    return files


def _iter_content_json_files(repo_root: pathlib.Path) -> list[pathlib.Path]:
    out = []
    for sub in CONTENT_DIRS:
        base = repo_root / sub
        if base.exists():
            out.extend(sorted(base.rglob("*.json")))
    return out


def _infer_schema_name(path: pathlib.Path) -> str | None:
    if "writing-systems" in path.parts:
        return "writing-system.schema.json"
    name = path.name.lower()
    if name == "metadata.json":
        return "language-metadata.schema.json"
    if "lexicon" in name:
        return "lexicon-entry.schema.json"
    if "example" in name or "sentence" in name:
        return "example-sentence.schema.json"
    if "writing" in name or "script" in name:
        return "writing-system.schema.json"
    if "curriculum" in name or "unit" in name:
        return "curriculum-unit.schema.json"
    if "heritage" in name:
        return "heritage-contribution.schema.json"
    if "scripture" in name or "bible" in name:
        return "scripture-bundle.schema.json"
    return None


def check_syntax_and_encoding(repo_root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for path in _iter_repo_files(repo_root):
        if path.suffix.lower() in {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".sqlite", ".db", ".enc"}:
            errors.append(f"{path.relative_to(repo_root)}: forbidden binary audio/database/encrypted asset")
            continue
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{path.relative_to(repo_root)}: contains UTF-8 BOM")
            continue
        if b"\r\n" in raw:
            errors.append(f"{path.relative_to(repo_root)}: contains CRLF line endings")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{path.relative_to(repo_root)}: invalid UTF-8 ({exc})")
            continue
        if text != unicodedata.normalize("NFC", text):
            errors.append(f"{path.relative_to(repo_root)}: not NFC normalized")
        if text and not text.endswith("\n"):
            errors.append(f"{path.relative_to(repo_root)}: missing trailing newline")
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.relative_to(repo_root)}: invalid JSON ({exc})")
        elif path.suffix.lower() in {".yml", ".yaml"} and yaml is not None:
            try:
                yaml.safe_load(text)
            except yaml.YAMLError as exc:
                errors.append(f"{path.relative_to(repo_root)}: invalid YAML ({exc})")
    return errors


def check_schemas(repo_root: pathlib.Path, schemas_dir: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for jf in _iter_content_json_files(repo_root):
        sname = _infer_schema_name(jf)
        if sname is None:
            errors.append(f"{jf.relative_to(repo_root)}: could not map JSON filename to an approved schema")
            continue
        schema_path = schemas_dir / sname
        if not schema_path.exists():
            errors.append(f"{jf.relative_to(repo_root)}: missing schema {schema_path}")
            continue
        data = json.loads(jf.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for err in _validate_schema_obj(data, schema):
            errors.append(f"{jf.relative_to(repo_root)}: {err}")
    return errors


def check_payload_rules(data: dict[str, Any], label: str, mode: str) -> list[str]:
    errors: list[str] = []
    if mode == "duplicates-and-spans":
        lang = data.get("language_code", "")
        seen_c: set[tuple[str, str]] = set()
        for idx, entry in enumerate(data.get("entries", [])):
            ck = entry.get("concept_key", "")
            if (lang, ck) in seen_c:
                errors.append(f"{label}: duplicate (language_code, concept_key) ({lang}, {ck})")
            seen_c.add((lang, ck))
            for ex_idx, ex in enumerate(entry.get("examples", [])):
                txt = ex.get("sentence_text", "")
                for tok in ex.get("tokens", []):
                    s, e, surf = tok.get("char_start"), tok.get("char_end"), tok.get("surface", "")
                    if not isinstance(s, int) or not isinstance(e, int) or not (0 <= s < e <= len(txt)) or txt[s:e] != surf:
                        errors.append(f"{label}: bad token span in entries[{idx}].examples[{ex_idx}]")
        for idx, sent in enumerate(data.get("sentences", [])):
            txt = sent.get("sentence_text", "")
            for tok in sent.get("tokens", []):
                s, e, surf = tok.get("char_start"), tok.get("char_end"), tok.get("surface", "")
                if not isinstance(s, int) or not isinstance(e, int) or not (0 <= s < e <= len(txt)) or txt[s:e] != surf:
                    errors.append(f"{label}: bad token span in sentences[{idx}]")
    elif mode == "provenance-and-license":
        lic = str(data.get("license", "") or data.get("licenseInfo", {}).get("license", "")).strip()
        if lic.upper() in DISALLOWED_LICENSE_VALUES:
            errors.append(f"{label}: disallowed license {lic!r}")
        cit = str(data.get("source_citation", "")).lower()
        for term in FORBIDDEN_CITATION_TERMS:
            if term in cit:
                errors.append(f"{label}: forbidden citation term {term!r}")
    elif mode == "anti-synthetic":
        def walk(node: Any, p: str) -> None:
            if isinstance(node, dict):
                for k in ("term", "normalized_term"):
                    val = node.get(k)
                    if isinstance(val, str) and SYNTHETIC_SUFFIX_RE.search(val.strip()):
                        errors.append(f"{label} {p}.{k}: synthetic numeric suffix {val!r}")
                for k, v in node.items():
                    walk(v, f"{p}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{p}[{i}]")
            elif isinstance(node, str):
                for pat in SYNTHETIC_TEXT_PATTERNS:
                    if pat.search(node.strip()):
                        errors.append(f"{label} {p}: synthetic/boilerplate pattern {pat.pattern!r}")
        walk(data, "$")
    return errors


def check_formatting(repo_root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for jf in sorted(repo_root.rglob("*.json")):
        if any(part in SKIP_DIRS for part in jf.parts):
            continue
        text = jf.read_text(encoding="utf-8")
        expected = json.dumps(json.loads(text), indent=2, ensure_ascii=False) + "\n"
        if text != expected:
            errors.append(f"{jf.relative_to(repo_root)}: not canonical 2-space LF JSON")
    return errors


def run_all_checks(check: str, repo_root: pathlib.Path = ROOT, schemas_dir: pathlib.Path | None = None) -> list[str]:
    sdir = schemas_dir or (repo_root / "schemas")
    errors: list[str] = []
    if check in {"syntax-and-encoding", "all"}:
        errors.extend(check_syntax_and_encoding(repo_root))
    if check in {"schema", "all"}:
        errors.extend(check_schemas(repo_root, sdir))
    for jf in _iter_content_json_files(repo_root):
        data = json.loads(jf.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for mode in ("duplicates-and-spans", "provenance-and-license", "anti-synthetic"):
                if check in {mode, "all"}:
                    errors.extend(check_payload_rules(data, str(jf.relative_to(repo_root)), mode))
    if check in {"formatting", "all"}:
        errors.extend(check_formatting(repo_root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Divinari Language Resources 7-Layer Validator")
    parser.add_argument(
        "--check",
        default="all",
        choices=[
            "all",
            "syntax-and-encoding",
            "schema",
            "duplicates-and-spans",
            "provenance-and-license",
            "anti-synthetic",
            "formatting",
        ],
    )
    parser.add_argument("--schemas-dir", default=str(ROOT / "schemas"))
    args = parser.parse_args()
    errs = run_all_checks(args.check, ROOT, pathlib.Path(args.schemas_dir))
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"PASS ({args.check}): zero issues detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
