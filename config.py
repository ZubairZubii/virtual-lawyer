"""
Project configuration.

This file is intentionally used by the backend pipelines to read API keys
and pipeline settings from environment variables / local `.env`.
"""

from __future__ import annotations

import os
from typing import Any, Dict

try:
    from dotenv import load_dotenv

    # Load variables from the project root `.env` (if present).
    load_dotenv()
except ModuleNotFoundError:
    # If `python-dotenv` isn't installed yet, we can still rely on
    # environment variables set by the shell.
    pass

# Groq API key used by the 2-stage / 3-stage formatting pipelines.
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# Default pipeline settings (used if the config is available to the pipelines).
PIPELINE_CONFIG: Dict[str, Any] = {
    "formatter_type": "groq",
    # Groq decommissioned `llama-3.1-70b-versatile`. Use a supported model.
    "formatter_model": "llama-3.3-70b-versatile",
    "stage1": {
        "max_new_tokens": 150,
        "temperature": 0.2,
        "top_k": 3,
        "context_max_length": 1500,
    },
    "stage2": {
        "temperature": 0.3,
        "max_tokens": 600,
        "top_p": 0.9,
    },
}

