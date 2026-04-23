"""
Structured pipeline tracing for chat (Stage 1 / 1.5 / 2).

Enable with env PIPELINE_TRACE=true (default). Set PIPELINE_TRACE=false to silence.
Set PIPELINE_TRACE=debug for extra verbosity.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger("virtual_lawyer.pipeline")
_CONFIGURED = False


def pipeline_trace_enabled() -> bool:
    v = os.getenv("PIPELINE_TRACE", "true").strip().lower()
    return v not in ("0", "false", "no", "off")


def pipeline_trace_debug() -> bool:
    return os.getenv("PIPELINE_TRACE", "").strip().lower() in ("debug", "2", "verbose")


def configure_pipeline_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True
    if not pipeline_trace_enabled():
        _LOGGER.disabled = True
        return
    level = logging.DEBUG if pipeline_trace_debug() else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    _LOGGER.handlers.clear()
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(level)
    _LOGGER.propagate = False


def _trunc(s: str, limit: int = 6000) -> str:
    s = s or ""
    if len(s) <= limit:
        return s
    return s[:limit] + f"\n... [{len(s) - limit} more chars truncated]"


def trace_block(title: str, fields: Dict[str, Any]) -> None:
    if not pipeline_trace_enabled():
        return
    lines = [f"\n{'=' * 20} {title} {'=' * 20}"]
    for key, val in fields.items():
        if val is None:
            continue
        if isinstance(val, (list, tuple)) and val and isinstance(val[0], dict):
            lines.append(f"-- {key} --")
            for i, item in enumerate(val[:12], 1):
                lines.append(f"  [{i}] {item}")
            continue
        text = val if isinstance(val, str) else repr(val)
        lines.append(f"-- {key} --")
        lines.append(_trunc(text))
    _LOGGER.info("\n".join(lines))


def scrub_statute_numbers_from_chat_answer(text: str) -> str:
    """
    Remove explicit section/article-style citations from text shown in chat.
    Detailed citations should appear only in Sources.
    """
    if not text:
        return text
    t = text
    t = re.sub(r"(?i)\b(?:crpc|ppc)\s+section\s+\d+[a-z]?\b", "", t)
    t = re.sub(
        r"(?i)\bsection\s+\d+[a-z]?\s+(?:of\s+)?(?:the\s+)?(?:ppc|crpc|penal\s+code|code\s+of\s+criminal\s+procedure)\b",
        "",
        t,
    )
    t = re.sub(r"(?i)\bsections?\s+\d+[a-z]?(?:\s*[-–]\s*\d+[a-z]?)?\b", "", t)
    t = re.sub(r"(?i)\bsection\s+\d+[a-z]?\b", "", t)
    t = re.sub(r"(?i)\barticle\s+\d+[a-z]?\b", "", t)
    t = re.sub(r"(?i)\bart\.\s*\d+\b", "", t)
    t = re.sub(r"(?i)\bss\s*\.?\s*\d+[a-z]?\b", "", t)
    t = re.sub(r"\(\s*\)", "", t)
    # Keep newlines intact; collapse only repeated spaces/tabs.
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"\s+([,.;:])", r"\1", t)
    t = re.sub(r"\s+\n", "\n", t)
    return t.strip()


def summarize_references(refs: Optional[List[Dict]]) -> List[str]:
    out: List[str] = []
    if not refs:
        return out
    for r in refs[:8]:
        if not isinstance(r, dict):
            continue
        bits = [str(r.get("type", "")), str(r.get("title", "") or r.get("case_no", "") or r.get("section", ""))]
        out.append(" | ".join(b for b in bits if b))
    return out


def summarize_retrieved_docs(docs: Optional[List[Dict]]) -> List[str]:
    out: List[str] = []
    if not docs:
        return out
    for d in docs[:8]:
        if not isinstance(d, dict):
            continue
        meta = d.get("metadata") or {}
        sec = meta.get("section_number") or meta.get("section") or ""
        title = (d.get("title") or "")[:120]
        dtype = d.get("type") or ""
        out.append(f"type={dtype} section={sec} title={title}")
    return out
