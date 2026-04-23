"""
Local Reasoning Enhancer (optional stage)

Pipeline role:
Extractive grounded answer -> local refinement/reasoning -> optional formatter

This module is intentionally optional and fault-tolerant:
- If model loading fails, pipeline falls back to extractive answer.
- Keeps deployment safe on machines without enough VRAM/RAM.
"""

from __future__ import annotations

import os
from typing import Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from transformers import BitsAndBytesConfig
except Exception:
    BitsAndBytesConfig = None


class LocalReasoningEnhancer:
    """Optional local reasoning/refinement stage using an instruct model."""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-3B-Instruct",
        max_input_tokens: int = 1400,
        max_new_tokens: int = 320,
        temperature: float = 0.2,
        top_p: float = 0.9,
    ):
        self.model_name = model_name
        self.max_input_tokens = max_input_tokens
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p

        self.tokenizer = None
        self.model = None
        self.available = False

        self._load()

    def _load(self) -> None:
        """Load tokenizer/model with conservative defaults."""
        try:
            print(f"Stage 1.5: Loading local reasoning model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            model_kwargs = {"device_map": "auto"}
            use_4bit = os.getenv("LOCAL_REASONER_4BIT", "true").lower() == "true"
            if use_4bit and BitsAndBytesConfig is not None:
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )

            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_kwargs)
            self.model.eval()
            self.available = True
            print("Stage 1.5 ready (local reasoning enhancer enabled)")
        except Exception as e:
            self.available = False
            self.tokenizer = None
            self.model = None
            print(f"Stage 1.5 unavailable, fallback to extractive answer: {e}")

    def _build_prompt(self, question: str, answer: str, references: List[Dict]) -> str:
        ref_lines = []
        for ref in references[:4]:
            if not isinstance(ref, dict):
                continue
            if ref.get("type") == "PPC" and ref.get("section"):
                ref_lines.append(f"- Section {ref.get('section')} PPC")
            elif ref.get("type") == "CrPC" and ref.get("title"):
                ref_lines.append(f"- {ref.get('title')}")
            elif ref.get("type") == "Constitution" and ref.get("title"):
                ref_lines.append(f"- {ref.get('title')}")
            elif ref.get("type") == "Case Law" and ref.get("case_no"):
                ref_lines.append(f"- Case: {ref.get('case_no')}")
            elif ref.get("title"):
                ref_lines.append(f"- {ref.get('title')}")

        refs = "\n".join(ref_lines) if ref_lines else "- No explicit references provided"
        return f"""You are a Pakistan criminal law reasoning assistant.
Task: refine the grounded draft into a reasoned answer: apply the cited law to the question's facts, then state practical implications.

GROUNDING LOCK (STRICT):
1) Use only information present in Grounded Draft and Grounded References.
2) Do not introduce any new section number, article, or case citation not listed.
3) If information is missing, explicitly write: "Not specified in extracted law."

REASONING REQUIREMENTS:
- Issue: One short paragraph stating the legal problem in plain words (from the question + draft).
- Legal Basis: Bullet or short list tying each listed reference to what it governs (only cited items).
- Analysis: Use IRAC flow (Rule -> Application -> Conclusion) with at least two short paragraphs.
- Conclusion: Directly answer the user question in first sentence (no generic disclaimer opener), then practical implication.

RULES:
1) Do not invent sections or citations.
2) Use only Pakistan law terms (PPC, CrPC, Constitution).
3) Preserve grounded legal content; expand reasoning, not new law.
4) Avoid copy-paste from draft; rewrite in concise plain language.

RETRIEVAL-REPAIR TASK (MANDATORY):
1) Remove weak/irrelevant references from reasoning narrative if they do not match facts.
2) If core law seems missing from references, add exactly one line: Retrieval gap: core law not fully captured in sources.
3) Do NOT invent section/case numbers to fill gaps.

Question:
{question}

Grounded Draft:
{answer}

Grounded References:
{refs}

Output format:
Issue:
Legal Basis:
Analysis:
Conclusion:
"""

    def enhance(self, question: str, answer: str, references: List[Dict]) -> str:
        """Enhance the draft answer, or return original if unavailable."""
        if not self.available or not self.model or not self.tokenizer:
            return answer

        prompt = self._build_prompt(question, answer, references)
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_input_tokens,
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=True,
                top_p=self.top_p,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        full = self.tokenizer.decode(out[0], skip_special_tokens=True)
        enhanced = full.split("Output format:", 1)[-1].strip() if "Output format:" in full else full.strip()
        if len(enhanced) < 40:
            return answer
        # Reject placeholder/empty-template outputs.
        if "Issue:\nLegal Basis:\nAnalysis:\nConclusion:" in enhanced.replace("\r\n", "\n"):
            return answer
        if "Not specified in extracted law." in enhanced and len(references) >= 1:
            return answer
        return enhanced

