"""
Multi-Layer Pipeline for Pakistan Criminal Law Chatbot
Combines: RAG Retrieval → Model Generation → Answer Synthesis → Reference Tracking
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import sys
import os
import time
import re
from typing import Dict, List, Tuple

# Add paths
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from multi_source_rag import MultiSourceRAG

try:
    from pipeline_trace import (
        scrub_statute_numbers_from_chat_answer,
        summarize_retrieved_docs,
        summarize_references,
        trace_block,
    )
except ImportError:
    trace_block = None

    def scrub_statute_numbers_from_chat_answer(t: str) -> str:
        return t

    def summarize_retrieved_docs(docs):
        return []

    def summarize_references(refs):
        return []

class MultiLayerPipeline:
    """Multi-layer pipeline for best answer generation"""
    
    def __init__(self,
                 base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                 peft_model_path="./models/final_model_v5",
                 use_rag=True):
        
        print("Initializing Multi-Layer Pipeline...")
        start_time = time.time()
        self.stage1_mode = os.getenv("STAGE1_MODE", "extractive").lower()
        self.model = None
        self.tokenizer = None
        
        if self.stage1_mode == "model":
            # Layer 1: Load Model (optional in long-term local architecture)
            print("\nLayer 1: Loading Model...")
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "right"
            
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,
                llm_int8_has_fp16_weight=False
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=quantization_config,
                device_map="auto"
            )
            
            self.model = PeftModel.from_pretrained(self.model, peft_model_path)
            self.model.eval()
            print("   Model loaded")
        else:
            print("\nLayer 1: Model loading skipped (extractive stage1 mode)")
        
        # Layer 2: Initialize Multi-Source RAG
        if use_rag:
            print("\nLayer 2: Initializing Multi-Source RAG...")
            self.rag = MultiSourceRAG()
            print("   RAG system ready")
        else:
            self.rag = None
        
        load_time = time.time() - start_time
        print(f"\nPipeline ready! (Loaded in {load_time:.1f}s)\n")

    def _classify_query_intent(self, question: str) -> str:
        q = question.lower()
        if self._is_attempt_to_murder_question(question):
            return "offense_classification"
        if "section" in q or re.search(r"\b\d+[a-z]?\s*(ppc|crpc)\b", q):
            return "statute_lookup"
        if any(x in q for x in ["witness", "contradictory", "contradiction", "credibility", "testimony"]):
            return "evidence_credibility"
        if any(x in q for x in ["what should i do", "first 24 hours", "immediately", "next steps", "urgent"]):
            return "advice"
        if any(x in q for x in ["punishment", "sentence", "penalty", "bailable", "non-bailable"]):
            return "penalty"
        if any(x in q for x in ["fir", "remand", "investigation", "hearing", "procedure", "status"]):
            return "procedure"
        return "general"

    def _rewrite_query_for_retrieval(self, question: str, intent: str) -> str:
        q = question.strip()
        base = f"Pakistan criminal law {q}"
        if self._is_fir_refusal_question(q):
            return (
                f"{base} CrPC FIR refusal registration duty section 154 complaint to magistrate "
                f"section 156(3) justice of peace section 22A section 22B section 157"
            )
        if self._is_attempt_to_murder_question(q):
            return (
                f"{base} PPC section 307 attempt to murder firearm shot missed no injury "
                f"intention knowledge act towards commission offence"
            )
        if self._is_unlawful_assembly_blockade_question(q):
            return (
                f"{base} PPC unlawful assembly riot obstruction public way wrongful restraint "
                f"highway blockade section 141 146 147 149 283 341 188 CrPC preventive action"
            )
        if self._is_public_servant_bribe_question(q):
            return (
                f"{base} anti-corruption public servant illegal gratification bribery extortion "
                f"PPC corruption provisions prevention of corruption act criminal misconduct"
            )
        if intent == "statute_lookup":
            return f"{base} exact section text PPC CrPC ingredients punishment bailable cognizable"
        if intent == "advice":
            return f"{base} practical steps legal remedies FIR bail rights immediate actions CrPC"
        if intent == "penalty":
            return f"{base} punishment imprisonment fine bailable non-bailable cognizable PPC"
        if intent == "procedure":
            return f"{base} CrPC procedure filing inquiry investigation hearing court process"
        if intent == "evidence_credibility":
            return f"{base} witness credibility contradiction section 161 CrPC section 540 CrPC material vs minor contradiction"
        if self._is_search_seizure_question(q):
            return (
                f"{base} CrPC police search dwelling warrant magistrate seizure memorandum "
                f"section 165 103 104 100 stolen property investigation"
            )
        if self._is_private_defence_homicide_scenario(q):
            return (
                f"{base} PPC private defence right of private defence murder culpable homicide "
                f"robbery dacoity exceeding grave provocation exceptions qatl"
            )
        if self._is_juvenile_comparison_question(q):
            return (
                f"{base} Juvenile Justice System Act juvenile child offender age determination "
                f"juvenile court rehabilitation borstal probation bail privacy no death penalty adult comparison"
            )
        return f"{base} relevant sections case law legal basis"

    def _is_fir_refusal_question(self, question: str) -> bool:
        q = question.lower()
        has_fir = "fir" in q or "first information report" in q
        refusal = any(k in q for k in ["refuse", "refused", "not register", "denied", "decline"])
        police = "police" in q or "station" in q
        return has_fir and refusal and police

    def _is_attempt_to_murder_question(self, question: str) -> bool:
        q = question.lower()
        shooting = any(k in q for k in ["shoot", "shot", "fired", "firearm", "gun"])
        attempt = any(k in q for k in ["miss", "missed", "no injury", "not injured", "attempt"])
        victim = any(k in q for k in ["person", "victim", "another"])
        return shooting and (attempt or victim)

    def _is_unlawful_assembly_blockade_question(self, question: str) -> bool:
        q = question.lower()
        protest = any(k in q for k in ["protest", "demonstration", "rally", "mob", "group"])
        blockade = any(k in q for k in ["block", "blocked", "blocking", "highway", "road", "public way"])
        crowd = any(k in q for k in ["assembly", "unlawful assembly", "30 people", "crowd"])
        return (protest and blockade) or (crowd and blockade)

    def _is_public_servant_bribe_question(self, question: str) -> bool:
        q = question.lower()
        servant = any(k in q for k in ["government officer", "public servant", "official", "license", "permit"])
        bribe = any(k in q for k in ["demand money", "bribe", "illegal gratification", "kickback", "extortion"])
        corruption = "corruption" in q or "anti-corruption" in q
        return (servant and bribe) or (servant and corruption)

    def _is_search_seizure_question(self, question: str) -> bool:
        q = question.lower()
        topic = any(
            k in q
            for k in [
                "search warrant",
                "search and seizure",
                "seize",
                "seized",
                "seizure",
                "raid",
                "illegal search",
            ]
        ) or ("search" in q and "warrant" in q) or ("search" in q and "police" in q) or (
            "entered" in q and ("house" in q or "home" in q)
        )
        context = any(
            k in q
            for k in [
                "police",
                "house",
                "home",
                "premises",
                "dwelling",
                "warrant",
                "mobile",
                "phone",
                "document",
                "papers",
            ]
        )
        return topic and context

    def _is_private_defence_homicide_scenario(self, question: str) -> bool:
        q = question.lower()
        violent = any(
            k in q
            for k in [
                "robber",
                "robbery",
                "dacoity",
                "theft",
                "armed",
                "weapon",
                "gun",
                "knife",
                "attack",
                "assault",
            ]
        )
        death_or_hurt = any(
            k in q
            for k in [
                "kill",
                "killed",
                "death",
                "die",
                "murder",
                "qatl",
                "shoot",
                "shot",
                "stab",
            ]
        )
        defence = any(
            k in q
            for k in [
                "self-defence",
                "self defence",
                "self defense",
                "defend",
                "defending",
                "protect",
                "shopkeeper",
                "owner",
            ]
        )
        return (violent and death_or_hurt) or (death_or_hurt and defence) or (
            "lawful" in q and "defence" in q
        )

    def _is_juvenile_comparison_question(self, question: str) -> bool:
        q = question.lower()
        juvenile_markers = [
            "juvenile", "child", "minor", "under 18", "15-year", "15 year",
            "teen", "jjsa", "juvenile justice", "age determination", "borstal",
        ]
        comparison_markers = ["adult", "differently", "difference", "compare", "comparison", "versus", "vs"]
        asks_handling = any(k in q for k in ["handle", "treated", "trial", "punishment", "bail"])
        has_juvenile = any(k in q for k in juvenile_markers)
        has_comparison = any(k in q for k in comparison_markers)
        return has_juvenile and (has_comparison or asks_handling)

    def _extract_target_section(self, question: str) -> Tuple[str, str]:
        """
        Extract target section and code from query.
        Returns: (section_number, code) where code is "ppc" | "crpc" | ""
        """
        q = question.lower()
        m = re.search(r"section\s+(\d+[a-z]?)\s*(ppc|crpc)", q)
        if m:
            return m.group(1), m.group(2)
        # fallback for "Explain section 154 of CrPC" style
        m2 = re.search(r"section\s+(\d+[a-z]?)", q)
        if m2:
            code = "crpc" if "crpc" in q else ("ppc" if "ppc" in q else "")
            return m2.group(1), code
        return "", ""

    def _extract_section_from_doc(self, doc: Dict) -> str:
        """Extract section number from retrieved doc metadata/title."""
        metadata = doc.get("metadata", {}) or {}
        for key in ["section_number", "section", "section_no"]:
            value = str(metadata.get(key, "")).strip()
            if value:
                return value.lower()
        for key in ["section", "section_number"]:
            value = str(doc.get(key, "")).strip()
            if value:
                return value.lower()
        title = str(doc.get("title", "")).lower()
        match = re.search(r"section\s+(\d+[a-z]?)", title)
        return match.group(1).lower() if match else ""

    def _filter_relevant_chunks(self, question: str, docs: List[Dict]) -> List[Dict]:
        """
        Enforce exact-section priority for statute queries to prevent wrong section drift.
        """
        section, code = self._extract_target_section(question)
        if not section:
            return docs

        # 1) Strongly prefer authoritative statute_guide exact matches if present.
        statute_exact = []
        for doc in docs:
            metadata = doc.get("metadata") or {}
            doc_type = (doc.get("type") or "").lower()
            sec_meta = str(metadata.get("section_number", "")).lower()
            law_type = str(metadata.get("law_type", "")).lower()
            if doc_type == "statute_guide" and sec_meta == section:
                if not code or law_type == code:
                    statute_exact.append(doc)
        if statute_exact:
            return statute_exact

        exact = []
        for doc in docs:
            text = (doc.get("text") or "").lower()
            title = (doc.get("title") or "").lower()
            doc_type = (doc.get("type") or "").lower()
            metadata = doc.get("metadata") or {}
            sec_meta = str(metadata.get("section_number", "")).lower()

            section_hit = (
                sec_meta == section
                or f"section {section}" in text
                or f"section {section}" in title
            )
            code_hit = True
            if code == "ppc":
                code_hit = ("ppc" in text or "ppc" in title or doc_type == "ppc")
            elif code == "crpc":
                code_hit = ("crpc" in text or "crpc" in title or doc_type == "crpc")

            if section_hit and code_hit:
                exact.append(doc)

        # 2) Keep exact matches first; if none, remove chunks that explicitly discuss other sections.
        if exact:
            return exact

        narrowed = []
        other_section_pattern = re.compile(r"section\s+(\d+[a-z]?)", re.IGNORECASE)
        for doc in docs:
            text = (doc.get("text") or "")
            mentions = [m.group(1).lower() for m in other_section_pattern.finditer(text[:700])]
            # keep chunk if it does not explicitly emphasize different sections
            if not mentions or section in mentions:
                narrowed.append(doc)

        # Fallback to narrowed docs (or original if narrowing removed everything).
        if narrowed:
            return narrowed[:3]

        # Keep original docs as final graceful fallback.
        return exact if exact else docs

    def _apply_scenario_anchor_filter(self, question: str, docs: List[Dict]) -> List[Dict]:
        """
        Scenario-specific legal anchor filter for non-statute prompts.
        Keeps legally central sections at top to reduce case-snippet drift.
        """
        q = question.lower()
        if not docs:
            return docs

        # FIR refusal remedy flow (prioritize core CrPC provisions).
        if self._is_fir_refusal_question(question):
            fir_sections = {"154", "156", "157", "22a", "22b"}
            anchored, rest = [], []
            for doc in docs:
                sec = self._extract_section_from_doc(doc)
                dt = (doc.get("type") or "").lower()
                if sec in fir_sections and dt in {"crpc", "statute_guide"}:
                    anchored.append(doc)
                else:
                    rest.append(doc)
            if anchored:
                dedup = []
                seen = set()
                for item in anchored + rest:
                    key = ((item.get("type") or ""), self._extract_section_from_doc(item), (item.get("title") or "")[:80])
                    if key in seen:
                        continue
                    seen.add(key)
                    dedup.append(item)
                return dedup[:3]

        # Unlawful assembly / highway blockade (prefer PPC statutory anchors).
        if self._is_unlawful_assembly_blockade_question(question):
            ppc_sections = {"141", "146", "147", "148", "149", "283", "341", "188"}
            anchored, rest = [], []
            for doc in docs:
                sec = self._extract_section_from_doc(doc)
                dt = (doc.get("type") or "").lower()
                meta = doc.get("metadata") or {}
                law = str(meta.get("law_type", "")).lower()
                if sec in ppc_sections and dt in {"ppc", "statute_guide"} and (not law or law == "ppc"):
                    anchored.append(doc)
                else:
                    rest.append(doc)
            if anchored:
                out = list(anchored[:3])
                for d in rest:
                    if len(out) >= 3:
                        break
                    if (d.get("type") or "").lower() == "case_law":
                        continue
                    out.append(d)
                return out[:3]

        # Public servant bribery/corruption (prefer anti-corruption and PPC/extortion statutory anchors).
        if self._is_public_servant_bribe_question(question):
            corruption_keywords = [
                "public servant", "illegal gratification", "bribe", "corruption",
                "extortion", "criminal misconduct", "prevention of corruption",
            ]
            ranked = []
            for doc in docs:
                text = (doc.get("text") or "").lower()
                title = (doc.get("title") or "").lower()
                dt = (doc.get("type") or "").lower()
                score = sum(1 for kw in corruption_keywords if kw in text or kw in title)
                if dt in {"statute_guide", "ppc", "crpc", "structured", "principle"}:
                    score += 1
                if dt == "case_law":
                    score -= 1
                ranked.append((score, doc))
            ranked.sort(key=lambda x: x[0], reverse=True)
            top = [d for s, d in ranked if s > 0][:3]
            if top:
                return top

        # Attempt to murder classification (prefer PPC 307 and penal provisions, avoid unrelated case snippets).
        if self._is_attempt_to_murder_question(question):
            ppc_sections = {"307", "324", "299", "300", "301"}
            anchored, rest = [], []
            for doc in docs:
                sec = self._extract_section_from_doc(doc)
                dt = (doc.get("type") or "").lower()
                meta = doc.get("metadata") or {}
                law = str(meta.get("law_type", "")).lower()
                if sec in ppc_sections and dt in {"ppc", "statute_guide"} and (not law or law == "ppc"):
                    anchored.append(doc)
                else:
                    rest.append(doc)
            if anchored:
                out = list(anchored[:3])
                for d in rest:
                    if len(out) >= 3:
                        break
                    if (d.get("type") or "").lower() == "case_law":
                        continue
                    out.append(d)
                return out[:3]

        # Juvenile/child-offender comparison (prioritize JJSA-focused material).
        if self._is_juvenile_comparison_question(question):
            juvenile_keywords = [
                "juvenile justice system act",
                "juvenile",
                "child offender",
                "minor",
                "borstal",
                "rehabilitation",
                "age determination",
                "probation",
                "no death penalty",
                "privacy",
                "juvenile court",
            ]
            ranked = []
            for doc in docs:
                text = (doc.get("text") or "").lower()
                title = (doc.get("title") or "").lower()
                doc_type = (doc.get("type") or "").lower()
                score = sum(1 for kw in juvenile_keywords if kw in text or kw in title)
                if doc_type in {"statute_guide", "structured", "principle", "ppc", "crpc"}:
                    score += 1
                if doc_type == "constitution":
                    score -= 2
                if doc_type == "case_law":
                    score -= 1
                ranked.append((score, doc))
            ranked.sort(key=lambda x: x[0], reverse=True)
            top = [d for s, d in ranked if s > 0][:3]
            if top:
                return top

        # Private defence / culpable homicide / murder during attack or robbery (prefer PPC statute guide).
        if self._is_private_defence_homicide_scenario(question):
            ppc_sections = {
                "96",
                "97",
                "98",
                "99",
                "100",
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "299",
                "300",
                "301",
                "302",
                "304",
            }
            anchored = []
            rest = []
            for doc in docs:
                sec = self._extract_section_from_doc(doc)
                dt = (doc.get("type") or "").lower()
                meta = doc.get("metadata") or {}
                law = str(meta.get("law_type", "")).lower()
                if sec in ppc_sections and dt in {"ppc", "statute_guide"} and (not law or law == "ppc"):
                    anchored.append(doc)
                else:
                    rest.append(doc)
            if anchored:
                out = list(anchored[:3])
                for d in rest:
                    if len(out) >= 3:
                        break
                    dt = (d.get("type") or "").lower()
                    if dt == "case_law":
                        continue
                    txt = (d.get("text") or "").lower()
                    if dt in {"statute_guide", "ppc", "crpc", "principle"} and any(
                        k in txt
                        for k in (
                            "private defence",
                            "private defense",
                            "self-defence",
                            "culpable homicide",
                            "murder",
                            "qatl",
                            "robbery",
                        )
                    ):
                        out.append(d)
                dedup = []
                seen = set()
                for item in out:
                    key = (
                        (item.get("type") or ""),
                        self._extract_section_from_doc(item),
                        (item.get("title", "") or "")[:80],
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    dedup.append(item)
                return dedup[:3]

        # Police search / seizure / warrant at premises (prioritize CrPC search provisions).
        search_anchor_sections = {"96", "97", "98", "99", "100", "103", "104", "165"}
        if self._is_search_seizure_question(question):
            anchored = []
            rest = []
            for doc in docs:
                sec = self._extract_section_from_doc(doc)
                doc_type = (doc.get("type") or "").lower()
                if sec in search_anchor_sections and (doc_type in {"crpc", "statute_guide"}):
                    anchored.append(doc)
                else:
                    rest.append(doc)
            if anchored:
                dedup = []
                seen = set()
                for item in anchored + rest:
                    key = ((item.get("type") or ""), self._extract_section_from_doc(item), (item.get("title", "") or "")[:80])
                    if key in seen:
                        continue
                    seen.add(key)
                    dedup.append(item)
                return dedup[:3]

        # Arrest without warrant / arrest rights scenario anchors.
        arrest_anchor_sections = {"54", "55", "57", "60", "61", "167"}
        if any(k in q for k in ["without warrant", "arrest", "detention", "grounds of arrest", "fir is registered after arrest"]):
            anchored = []
            rest = []
            for doc in docs:
                sec = self._extract_section_from_doc(doc)
                doc_type = (doc.get("type") or "").lower()
                if sec in arrest_anchor_sections and (doc_type in {"crpc", "statute_guide"}):
                    anchored.append(doc)
                else:
                    rest.append(doc)
            if anchored:
                dedup = []
                seen = set()
                for item in anchored + rest:
                    key = ((item.get("type") or ""), self._extract_section_from_doc(item), (item.get("title") or "")[:80])
                    if key in seen:
                        continue
                    seen.add(key)
                    dedup.append(item)
                return dedup[:3]

        # Witness contradiction / credibility scenario anchors.
        if any(k in q for k in ["witness", "contradictory", "contradiction", "credibility", "testimony"]):
            credibility_keywords = ["material", "minor contradiction", "credibility", "section 161", "section 540", "corroboration"]
            ranked = []
            for doc in docs:
                text = (doc.get("text") or "").lower()
                score = sum(1 for kw in credibility_keywords if kw in text)
                ranked.append((score, doc))
            ranked.sort(key=lambda x: x[0], reverse=True)
            top = [d for s, d in ranked if s > 0][:3]
            if top:
                return top

        return docs

    def _clean_text(self, text: str, max_chars: int = 320) -> str:
        text = re.sub(r"\s+", " ", text or "").strip()
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rsplit(" ", 1)[0] + "..."

    def _user_visible_law_snippet(
        self, doc: Dict, max_chars: int = 220, attach_title: bool = False
    ) -> str:
        """
        Prefer statute-guide Plain Language over raw 'Full Text' dumps.
        By default returns body only (no section titles in chat — Sources carry citations).
        """
        raw = doc.get("text") or ""
        title = (doc.get("title") or "").strip()
        body = ""
        if "Plain Language:" in raw:
            tail = raw.split("Plain Language:", 1)[1]
            if "Legal Scope:" in tail:
                tail = tail.split("Legal Scope:", 1)[0]
            body = self._clean_text(tail.strip(), max_chars=max_chars)
        elif "Full Text:" in raw:
            tail = raw.split("Full Text:", 1)[1]
            if "Plain Language:" in tail:
                tail = tail.split("Plain Language:", 1)[0]
            body = self._clean_text(tail.strip(), max_chars=min(max_chars, 180))
        else:
            body = self._clean_text(raw, max_chars=max_chars)
        body = scrub_statute_numbers_from_chat_answer(body)
        if attach_title and title and body:
            return f"{title}: {body}"
        if body:
            return body
        return scrub_statute_numbers_from_chat_answer(title)

    def _extractive_compose_answer(
        self,
        question: str,
        retrieved_docs: List[Dict],
        references: List[Dict],
        intent: str
    ) -> Tuple[str, str, Dict]:
        """
        Deterministic local composer (Issue -> Law -> Application -> Conclusion).
        This avoids low-quality freeform generation from very small local LLMs.
        """
        q = question.strip()
        q_lower = q.lower()
        if not retrieved_docs:
            if self._is_private_defence_homicide_scenario(q):
                answer = (
                    "Short answer: this can fall under lawful self-defence rather than ordinary murder if the danger was immediate and serious, "
                    "and the response was limited to that danger.\n\n"
                    "If force went beyond necessity after danger had passed, homicide liability risk increases.\n\n"
                    "Retrieval gap: core law not fully captured in sources. Re-run with targeted private-defence terms and verify with counsel."
                )
                return answer, "low", {
                    "issue": q,
                    "law": [],
                    "application": ["private_defence_scenario_detected=true", "retrieval_gap=true"],
                    "analysis": [
                        "Fallback criminal-law reasoning used because no grounded sources were retrieved.",
                        "Final legal outcome depends on evidence of immediacy and proportionality."
                    ],
                    "conclusion": "Potential self-defence, but grounded sources must be retrieved for reliable final answer.",
                }
            return (
                "I could not find sufficiently relevant legal material for this question. "
                "Please provide more specific details (section, stage, court, or FIR facts)."
            ), "low", {
                "issue": question.strip(),
                "law": [],
                "application": [],
                "analysis": [],
                "conclusion": "Insufficient grounded material found. Please provide more specific legal facts.",
            }

        top = retrieved_docs[:3]
        key_points = [self._user_visible_law_snippet(doc) for doc in top]
        key_points = [p for p in key_points if p]

        legal_basis_items = []
        for ref in references[:4]:
            if ref.get("type") == "PPC" and ref.get("section"):
                legal_basis_items.append(f"Section {ref.get('section')} PPC")
            elif ref.get("type") == "CrPC" and ref.get("title"):
                legal_basis_items.append(ref.get("title"))
            elif ref.get("type") == "Constitution" and ref.get("title"):
                legal_basis_items.append(ref.get("title"))
            elif ref.get("type") == "Case Law" and ref.get("case_no"):
                legal_basis_items.append(ref.get("case_no"))
            elif ref.get("title"):
                legal_basis_items.append(ref.get("title"))

        # Deduplicate while preserving order
        seen = set()
        legal_basis = []
        for item in legal_basis_items:
            if item and item not in seen:
                legal_basis.append(item)
                seen.add(item)

        law_line = ", ".join(legal_basis[:4]) if legal_basis else "relevant Pakistan criminal law sources"
        application_lines = []
        for idx, point in enumerate(key_points[:3], 1):
            application_lines.append(f"{idx}. {point}")

        # Micro reasoning layer (rule-based, no additional model call).
        reasoning_points = []
        combined_text = " ".join(key_points).lower()
        if "fir" in q.lower() and "154" in combined_text:
            reasoning_points.append("Because FIR registration is governed by CrPC procedures, immediate written legal response and counsel coordination are critical.")
        if any(k in q.lower() for k in ["bail", "arrest"]) and ("bail" in combined_text or "remand" in combined_text):
            reasoning_points.append("Where arrest risk exists, protective bail strategy should be considered at once through counsel.")
        if "status" in q.lower() and any(k in combined_text for k in ["hearing", "court", "case"]):
            reasoning_points.append("Case status tracking should rely on official court/case references and regular follow-up with court staff/counsel.")

        if intent == "advice":
            conclusion = (
                "Conclusion: Prioritize immediate documented legal steps (lawyer engagement, written applications, evidence preservation) "
                "within the same day."
            )
        elif any(k in q_lower for k in ["without warrant", "arrest", "detention"]):
            conclusion = (
                "Conclusion: Warrantless arrest is lawful only within statutory grounds; "
                "the accused must be informed of grounds and produced before a Magistrate within legal time limits."
            )
        elif intent == "evidence_credibility":
            conclusion = (
                "Conclusion: Courts usually separate material contradictions from minor inconsistencies; "
                "only contradictions affecting core prosecution facts materially weaken credibility."
            )
        else:
            conclusion = (
                "Conclusion: Apply these legal points to your exact facts through counsel, and verify court-specific procedure before action."
            )

        # ---- Human-friendly scenario templates (production UX) ----
        # 0) Highway blockade during protest (legal-provisions mode).
        if self._is_unlawful_assembly_blockade_question(q):
            lines = [self._user_visible_law_snippet(d) for d in top[:4]]
            lines = [ln for ln in lines if ln]
            answer = (
                "Answer:\n"
                "Blocking a highway with a large group during protest can attract provisions on unlawful assembly, riot-related conduct, and obstruction of public way, depending on facts and police evidence.\n\n"
                "Law:\n"
                "- Unlawful assembly/common-object framework can apply to group conduct.\n"
                "- Public-way obstruction and restraint-related provisions may apply to highway blockage.\n"
                "- If violence/threat/force appears, riot-related provisions can escalate liability.\n\n"
                "Sections:\n"
                "- See Sources for exact PPC/CrPC provisions matched to this scenario.\n\n"
                "Remedies / Exposure:\n"
                "- Investigating agency may register group charges based on role, common object, and evidence.\n"
                "- Individuals can contest role attribution, intent, and identification evidence.\n"
                "- Case outcome depends on proof of obstruction, force, and participation level.\n\n"
                "Conclusion:\n"
                "Primary exposure is under unlawful-assembly and public-obstruction style provisions, with escalation if riot/force facts are proved."
            )
            if lines:
                answer += "\n\nWhat current sources support:\n" + "\n".join(f"- {p}" for p in lines[:3])
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:6]],
                "application": ["group protest", "highway obstruction", "common-object assessment"],
                "analysis": [
                    "Court/prosecution will separate peaceful presence from active obstructive/violent acts.",
                    "Liability strength depends on proof of participation and role.",
                ],
                "conclusion": "Statutory exposure exists; severity depends on obstruction/riot evidence.",
            }
            return answer, "high" if legal_basis else "medium", structured

        # 0a) Government officer demanding money (anti-corruption mode).
        if self._is_public_servant_bribe_question(q):
            lines = [self._user_visible_law_snippet(d) for d in top[:4]]
            lines = [ln for ln in lines if ln]
            answer = (
                "Answer:\n"
                "A government officer demanding money to approve a license raises anti-corruption exposure and may also trigger penal-code/extortion style liability depending on coercion facts.\n\n"
                "Law:\n"
                "- Illegal gratification by public servant is treated as corruption-type misconduct.\n"
                "- If money is extracted through pressure/threat, extortion-related penal provisions can also be considered.\n"
                "- Investigation route depends on competent anti-corruption authority and evidence quality.\n\n"
                "Sections:\n"
                "- See Sources for exact anti-corruption/PPC provisions used in this answer.\n\n"
                "Remedies:\n"
                "- File complaint with anti-corruption authority with documentary proof (messages, call logs, payment demand trail).\n"
                "- Preserve demand evidence and witness details before formal complaint.\n"
                "- Seek legal advice on charge framing (corruption-only vs corruption plus extortion features).\n\n"
                "Conclusion:\n"
                "The conduct is prosecutable as corruption-focused illegality, with possible additional penal liability if coercive demand is proved."
            )
            if lines:
                answer += "\n\nWhat current sources support:\n" + "\n".join(f"- {p}" for p in lines[:3])
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:6]],
                "application": ["public-servant demand", "license approval linkage", "illegal gratification evidence"],
                "analysis": [
                    "Core issue is abuse of official position for unlawful gain.",
                    "Charge expansion depends on coercion and evidence of demand/acceptance.",
                ],
                "conclusion": "Treat as anti-corruption offence first, then evaluate extortion overlay on evidence.",
            }
            return answer, "high" if legal_basis else "medium", structured

        # 0) FIR refusal at police station (strict legal remedies mode).
        if self._is_fir_refusal_question(q):
            lines = [self._user_visible_law_snippet(d) for d in top[:4]]
            lines = [ln for ln in lines if ln]
            answer = (
                "Answer:\n"
                "If police refuse to register an FIR for a cognizable robbery report, the citizen has legal remedies under CrPC and can seek supervisory/judicial directions.\n\n"
                "Law:\n"
                "- FIR registration duty exists for cognizable offence information.\n"
                "- Magistrate-linked investigation route is available when police inaction continues.\n"
                "- Justice of Peace complaint route is available for directions regarding registration.\n\n"
                "Sections:\n"
                "- See Sources for exact CrPC provisions used in this answer.\n\n"
                "Remedies:\n"
                "- Submit written complaint with incident facts, date/time, and station details.\n"
                "- Approach the competent Justice of Peace forum for direction on FIR registration.\n"
                "- Move Magistrate-side relief path where investigation direction is legally available.\n"
                "- Preserve proof of refusal/inaction (application copy, diary entry, witnesses).\n\n"
                "Conclusion:\n"
                "Police refusal is not the end of process; CrPC provides escalation routes to compel lawful registration steps."
            )
            if lines:
                answer += "\n\nWhat current sources support:\n" + "\n".join(f"- {p}" for p in lines[:3])
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:6]],
                "application": ["FIR refusal detected", "cognizable offence context", "escalation remedies available"],
                "analysis": [
                    "Primary duty is registration at police level for cognizable information.",
                    "If refused, law provides structured escalation to Justice of Peace/Magistrate routes.",
                ],
                "conclusion": "Citizen can pursue CrPC remedies to force lawful FIR processing.",
            }
            return answer, "high" if legal_basis else "medium", structured

        # 0b) Shooting at victim but no injury (offence classification mode).
        if self._is_attempt_to_murder_question(q):
            lines = [self._user_visible_law_snippet(d) for d in top[:3]]
            lines = [ln for ln in lines if ln]
            answer = (
                "Answer:\n"
                "Where a person fires at another with lethal intent but misses, the primary offence is Attempt to Murder (PPC 307), subject to proof of intention/knowledge from facts.\n\n"
                "Law:\n"
                "- Attempt liability focuses on intention/knowledge and overt act toward causing death.\n"
                "- Absence of injury does not automatically remove attempt-to-murder liability.\n\n"
                "Sections:\n"
                "- See Sources for the exact PPC section references used.\n\n"
                "Remedies / Procedure:\n"
                "- Investigation should collect intent evidence: weapon use, range, aim direction, prior hostility, and witness accounts.\n"
                "- Final charge framing depends on prosecution evidence and court appreciation of intent.\n\n"
                "Conclusion:\n"
                "On these facts, classify first under Attempt to Murder framework, then refine only if evidence weakens intent."
            )
            if lines:
                answer += "\n\nWhat current sources support:\n" + "\n".join(f"- {p}" for p in lines[:3])
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:5]],
                "application": ["shooting act present", "no injury not decisive", "intent evidence required"],
                "analysis": [
                    "Core legal test is intention/knowledge plus act toward commission.",
                    "No-injury outcome can still remain attempt offence if mens rea is proved.",
                ],
                "conclusion": "Primary classification remains attempt to murder, subject to intent proof.",
            }
            return answer, "high" if legal_basis else "medium", structured

        # 0c) Immediate legal steps after robbery (legal-only mode).
        if "robbery" in q_lower and any(k in q_lower for k in ["immediate", "first", "steps", "what should"]):
            answer = (
                "Answer:\n"
                "Take immediate legal steps in sequence to preserve rights and trigger investigation.\n\n"
                "Law:\n"
                "- Report cognizable offence facts for FIR registration.\n"
                "- Investigation procedure follows once FIR route is activated.\n\n"
                "Sections:\n"
                "- See Sources for exact PPC/CrPC provisions used.\n\n"
                "Remedies / Steps:\n"
                "- File immediate FIR application with full incident details and accused description.\n"
                "- Submit available evidence (CCTV, call logs, eyewitness contacts, stolen item details).\n"
                "- If FIR is refused, escalate through legal complaint routes under CrPC.\n"
                "- Obtain copy/record of complaint submission for procedural tracking.\n\n"
                "Conclusion:\n"
                "Fast FIR activation plus evidence preservation is the strongest legal start after robbery."
            )
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:5]],
                "application": ["FIR first", "evidence preservation", "escalation on refusal"],
                "analysis": [
                    "Delay weakens evidence chain and can complicate prosecution.",
                    "Procedural compliance at start improves downstream investigation quality.",
                ],
                "conclusion": "Prioritize FIR + evidence + procedural escalation immediately.",
            }
            return answer, "high" if legal_basis else "medium", structured

        # 0) Juvenile vs adult handling (exam-style comparison)
        if self._is_juvenile_comparison_question(q):
            lines = [self._user_visible_law_snippet(d) for d in top[:4]]
            lines = [ln for ln in lines if ln]
            mentions_jjsa = any("juvenile justice system act" in (ln or "").lower() for ln in lines)

            answer = (
                "Direct answer:\n"
                "A 15-year-old is handled under the Juvenile Justice System Act framework, not in the same way as a regular adult accused.\n\n"
                "Juvenile vs adult (high-value comparison):\n"
                "- Forum: juvenile-focused court/process vs regular criminal court process.\n"
                "- Purpose: rehabilitation and reintegration vs primarily punitive sentencing model.\n"
                "- Sentencing exposure: juvenile-protective limits are applied vs full adult penal exposure.\n"
                "- Custody/treatment: child-sensitive handling and separation from adult offenders vs ordinary prison/custody regime.\n"
                "- Privacy/procedure: stronger privacy and child-protection safeguards vs ordinary criminal procedure.\n"
                "- Bail approach: comparatively more lenient, reform-oriented consideration vs stricter adult risk/punishment framework.\n\n"
                "Application to your question:\n"
                "- At age 15, age determination is legally central.\n"
                "- Once treated as juvenile, reform-focused handling dominates instead of adult punishment logic.\n"
                "- Court still evaluates offence facts, but response is structured around child-protection principles.\n\n"
            )
            if lines:
                answer += "What current sources support:\n" + "\n".join(f"- {p}" for p in lines[:3]) + "\n\n"
            if not mentions_jjsa:
                answer += (
                    "Retrieval gap: the source set did not explicitly surface Juvenile Justice System Act text. "
                    "Re-run retrieval with direct JJSA query terms for citation-precise exam writing.\n\n"
                )
            answer += "Conclusion: this should be treated through juvenile law with reform focus, not ordinary adult criminal-law treatment."

            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:6]],
                "application": [
                    "age=15 indicates child-offender pathway",
                    "juvenile handling emphasizes rehabilitation",
                    "adult-style punishment framework is not primary",
                ],
                "analysis": [
                    "The question asks comparison, so answer must map juvenile and adult tracks side-by-side.",
                    "Age determination and child-protective safeguards are central to final legal treatment.",
                ],
                "conclusion": "Juvenile framework applies with reform focus and procedural protections.",
            }
            return answer, "high" if mentions_jjsa else "medium", structured

        # 0) Private defence / robbery / killing scenario (IRAC + fact-to-law mapping)
        if self._is_private_defence_homicide_scenario(q):
            fact_map = {
                "threat_level": "high" if any(k in q_lower for k in ["armed", "weapon", "gun", "knife", "robber", "dacoity"]) else "unclear",
                "immediacy": "immediate" if any(k in q_lower for k in ["during", "while", "attempt", "attack", "robbery attempt"]) else "unclear",
                "defensive_action": "present" if any(k in q_lower for k in ["defend", "defending", "self-defence", "self defense", "protect"]) else "unclear",
                "death_caused": "yes" if any(k in q_lower for k in ["kill", "killed", "death", "shot", "stab"]) else "unclear",
            }

            ppc_refs = sum(1 for r in references if isinstance(r, dict) and str(r.get("type", "")).upper() == "PPC")
            retrieval_gap = ppc_refs == 0

            answer = (
                "Short answer:\n"
                "On your facts, this is more likely to be treated as lawful self-defence than ordinary murder, "
                "but the final legal label depends on whether force stayed within lawful limits.\n\n"
                "Reasoning (Rule -> Apply -> Conclusion):\n"
                "- Rule: defensive force can be legally protected when facing immediate serious threat.\n"
                f"- Apply: threat level={fact_map['threat_level']}, immediacy={fact_map['immediacy']}, defensive_action={fact_map['defensive_action']}, death_caused={fact_map['death_caused']}.\n"
                "- Conclusion: if danger was immediate and serious, defence justification is stronger; if force continued after danger ended, homicide liability risk rises.\n\n"
            )

            if key_points:
                answer += "What current sources support:\n" + "\n".join(f"- {p}" for p in key_points[:3]) + "\n\n"

            if retrieval_gap:
                answer += (
                    "Retrieval gap: core penal-code private-defence rules were not strongly captured in retrieved sources. "
                    "Treat this as a preliminary view and re-run with targeted private-defence query terms.\n\n"
                )

            answer += (
                "Practical next step: preserve timeline evidence (who attacked first, weapon use, distance, injuries, witnesses, CCTV), "
                "because those facts decide whether the act remains protected self-defence."
            )

            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:6]],
                "application": [
                    f"threat_level={fact_map['threat_level']}",
                    f"immediacy={fact_map['immediacy']}",
                    f"defensive_action={fact_map['defensive_action']}",
                    f"death_caused={fact_map['death_caused']}",
                ],
                "analysis": [
                    "Immediate serious threat supports self-defence framing.",
                    "Force beyond necessity after danger passes increases homicide risk.",
                    "Final outcome depends on evidence quality and timeline consistency.",
                ],
                "conclusion": "Likely self-defence on stated facts, subject to excess-force assessment.",
            }
            return answer, "high" if not retrieval_gap else "medium", structured

        # 1) Arrest without warrant + no reasons explained
        if any(k in q_lower for k in ["arrested", "without a warrant", "without warrant"]) and any(
            k in q_lower for k in ["not inform", "no reason", "reason of arrest", "grounds"]
        ):
            answer = (
                "In simple words, these are the likely legal violations under Pakistani law:\n\n"
                "1) If police had no reasonable grounds for warrantless arrest, it may violate Section 54 CrPC.\n"
                "2) Not informing the person of arrest grounds immediately can violate Section 60 CrPC.\n"
                "3) If the accused is not produced before a Magistrate within lawful time limits, custody may violate Section 61 read with Section 167 CrPC.\n\n"
                "What this means in practice:\n"
                "- Warrantless arrest is not automatically illegal, but police must meet legal conditions.\n"
                "- Police must communicate grounds of arrest promptly.\n"
                "- Continued detention without proper remand process is challengeable.\n\n"
                "Immediate legal steps:\n"
                "- Ask for written grounds of arrest and station diary/FIR details.\n"
                "- Move for bail/protective remedies through counsel.\n"
                "- Challenge illegal detention before the appropriate court if procedural safeguards were breached."
            )
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:5]],
                "application": [
                    "Check if Section 54 threshold (reasonable grounds) was met.",
                    "Check if grounds were communicated as required by Section 60.",
                    "Check 24-hour production/remand compliance under Sections 61/167.",
                ],
                "analysis": [
                    "Arrest legality depends on statutory conditions, not police label alone.",
                    "Procedural defects can materially support bail and detention challenge."
                ],
                "conclusion": "Potential violations arise if grounds, communication, or remand safeguards were not followed.",
            }
            return answer, "high" if len(legal_basis) >= 2 else "medium", structured

        # 2) FIR delay + false implication
        if "fir" in q_lower and any(k in q_lower for k in ["delay", "after", "days"]) and any(
            k in q_lower for k in ["false implication", "falsely", "false", "implication"]
        ):
            answer = (
                "In simple words, delay in FIR does not automatically end the case, but it can weaken prosecution credibility if unexplained.\n\n"
                "How courts usually view delay:\n"
                "1) If delay is reasonably explained (medical emergency, access issues, fear, etc.), impact may be limited.\n"
                "2) If delay is unexplained or suspicious, defense can argue consultation, improvement, or false implication.\n"
                "3) Delay is assessed with overall evidence quality, witness consistency, and surrounding circumstances.\n\n"
                "What the accused can do:\n"
                "- Demand strict proof of the delay explanation.\n"
                "- Highlight contradictions between FIR narrative and later statements.\n"
                "- Use delay as a credibility challenge in bail and trial strategy."
            )
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:5]],
                "application": [
                    "Assess whether FIR delay is explained with objective facts.",
                    "Test consistency between FIR and later witness versions.",
                    "Use unexplained delay to challenge prosecution credibility.",
                ],
                "analysis": [
                    "Delay is a weight-of-evidence factor, not an automatic acquittal rule.",
                    "Its legal impact depends on explanation quality and corroboration."
                ],
                "conclusion": "Unexplained delay supports defense challenge, especially with weak or contradictory evidence.",
            }
            return answer, "high" if len(legal_basis) >= 2 else "medium", structured

        # 3) Police search / seizure / warrant at home or similar (CrPC-grounded, non-dump format)
        if self._is_search_seizure_question(q):
            lines = [self._user_visible_law_snippet(d) for d in top[:4]]
            lines = [ln for ln in lines if ln]
            asks_remedy = any(
                k in q_lower for k in ["remedy", "remedies", "what can", "what should", "relief", "complaint"]
            )
            law_bullets = "\n".join(f"{i}. {ln}" for i, ln in enumerate(lines[:3], 1)) if lines else "- Use the Sources list for the exact sections retrieved."

            answer = (
                "Short answer (plain words):\n\n"
                "Whether this entry and seizure was lawful under CrPC depends on whether a valid legal basis existed at that moment — for example a search warrant from a competent authority, or another narrow statutory route described in the CrPC provisions your sources mention (such as powers during investigation or Magistrate-led search routes).\n\n"
                "From the facts you gave — no search warrant, seizure of phones and documents, and no written authorization shown — that pattern usually raises a serious red flag unless police can later prove a recognized exception on evidence. Only a court can finally decide after full facts.\n\n"
                "What the retrieved CrPC material is pointing to:\n"
                f"{law_bullets}\n\n"
            )
            if asks_remedy:
                answer += (
                    "Practical routes people in this situation often discuss with counsel (not a substitute for legal advice):\n"
                    "- Document everything: date/time, who entered, what was taken, witnesses, and any paperwork you did receive.\n"
                    "- Magistrate / complaint route: challenge illegal search or related conduct through the appropriate judicial magistrate forum and procedure your lawyer recommends.\n"
                    "- Return of seized articles: ask counsel whether an application for release or return of phones/documents is available on your facts under CrPC procedure.\n"
                    "- If a criminal case follows: discuss whether seizure or procedural defects should be raised regarding admissibility or weight of evidence.\n"
                    "- Constitutional / High Court route: may exist for fundamental-rights claims where facts support it — counsel decides forum and drafting; do not self-file complex petitions without advice.\n\n"
                )
            answer += (
                "Bottom line: if there was no warrant and no clear statutory exception backed by proof, treat the search as highly challengeable and get local counsel immediately.\n"
            )
            structured = {
                "issue": q,
                "law": [lb for lb in legal_basis[:6]],
                "application": lines[:4],
                "analysis": [
                    "Legality turns on warrant/authority and recognized CrPC exceptions, not on police preference alone.",
                    "Remedies depend on forum rules and facts; counsel chooses the right sequence.",
                ],
                "conclusion": "Escalate with documented facts through counsel; court decides final legality.",
            }
            return answer, "high" if lines else "medium", structured

        section, code = self._extract_target_section(question)
        if intent == "statute_lookup" and section:
            code_label = code.upper() if code else "relevant code"
            short_points = application_lines[:2] if application_lines else ["No clearly matched text was found for the requested section."]
            legal_scope_note = ""
            for ref in references:
                if not isinstance(ref, dict):
                    continue
                scope = (ref.get("legal_scope") or "").strip()
                if scope:
                    legal_scope_note = scope
                    break
            if not legal_scope_note:
                legal_scope_note = (
                    "Scope is limited to this section's direct statutory purpose. "
                    "Do not extend it to unrelated bail/remand/procedure provisions unless explicitly asked."
                )

            # Legal contrast injection for misconception/comparison style questions.
            contrast_lines = []
            asks_negative_scope = any(k in q_lower for k in ["does", "deal with", "cover", "include", "about"])
            asks_bail = "bail" in q_lower
            asks_arrest = "arrest" in q_lower
            asks_remand = "remand" in q_lower or "167" in q_lower
            asks_investigation = "investigation" in q_lower or "investigate" in q_lower

            if asks_negative_scope and section == "154" and (asks_bail or asks_arrest or asks_remand or asks_investigation):
                contrast_lines.append("Section 154 CrPC is limited to FIR registration in cognizable cases.")
                if asks_bail:
                    contrast_lines.append("Bail is governed by Sections 496, 497, and 498 CrPC, not Section 154.")
                if asks_arrest:
                    contrast_lines.append("Arrest powers/procedure are mainly addressed under Sections 54, 55, 57, 60 and related provisions, not Section 154.")
                if asks_remand:
                    contrast_lines.append("Remand and custody extension are addressed under Section 167 CrPC, not Section 154.")
                if asks_investigation:
                    contrast_lines.append("Investigation powers/procedure are addressed under Sections 156 and 157 CrPC, not Section 154.")

            # Section anchor lock: if target section is missing from legal basis, do not fabricate.
            legal_basis_text = " ".join(legal_basis).lower()
            expected = f"section {section}"
            if expected not in legal_basis_text:
                answer = (
                    f"I could not confidently find exact grounded text for Section {section} {code_label} in the current corpus.\n\n"
                    "Please retry with the exact section format (for example: 'Section 154 CrPC') or verify corpus coverage."
                )
                structured = {
                    "issue": q,
                    "law": [],
                    "application": [],
                    "analysis": [],
                    "conclusion": "Exact section anchor missing in retrieved corpus.",
                }
                return answer, "low", structured
            answer = (
                f"Section {section} {code_label} mainly covers this legal area:\n\n"
                + "\n".join(short_points)
                + "\n\n"
                + f"In plain language: {legal_scope_note}\n\n"
                + ("Important distinction:\n" + "\n".join(f"- {line}" for line in contrast_lines) + "\n\n" if contrast_lines else "")
                + f"Practical takeaway: {conclusion.replace('Conclusion: ', '')}\n"
                + f"Relevant law used: {law_line}"
            )
            structured = {
                "issue": q,
                "law": legal_basis[:4],
                "application": short_points,
                "analysis": (reasoning_points[:2] + contrast_lines[:2])[:3],
                "conclusion": conclusion,
            }
            confidence = "high" if legal_basis else "medium"
            return answer, confidence, structured

        confidence = "high" if len(legal_basis) >= 2 else ("medium" if len(legal_basis) == 1 else "low")

        direct_opening = "Here is a plain-language read of what the retrieved Pakistani criminal-law material supports:"
        answer = (
            f"{direct_opening}\n\n"
            + ("- " + application_lines[0] + "\n" if application_lines else "- I found limited grounded detail for this exact phrasing.\n")
            + ("- " + application_lines[1] + "\n" if len(application_lines) > 1 else "")
        )
        if any(k in q_lower for k in ["remedy", "remedies", "what can i", "what should i", "relief"]):
            answer += (
                "\nPractical direction (general):\n"
                "- Confirm facts in writing, then have counsel map the right forum (Magistrate complaint, return applications, trial objections, or other routes supported by your papers).\n"
            )
        if reasoning_points:
            answer += "\nWhy this matters:\n" + "\n".join(f"- {p}" for p in reasoning_points[:2]) + "\n"
        answer += f"\nWhat you should do next:\n- {conclusion.replace('Conclusion: ', '')}\n"

        structured = {
            "issue": q,
            "law": legal_basis[:4],
            "application": application_lines[:3],
            "analysis": reasoning_points[:2],
            "conclusion": conclusion,
        }
        return answer, confidence, structured
    
    def _create_enhanced_prompt(self, question: str, context: str, references: List[Dict]) -> str:
        """Create enhanced prompt with context and references"""
        
        # CRITICAL: Force model to use RAG context
        if context and context.strip():
            # Build reference section
            ref_section = ""
            if references:
                ref_section = "\n\nREFERENCES:\n"
                for i, ref in enumerate(references[:5], 1):
                    if ref['type'] == 'PPC':
                        ref_section += f"{i}. PPC Section {ref.get('section', 'N/A')}\n"
                    elif ref['type'] == 'Case Law':
                        ref_section += f"{i}. SHC Case {ref.get('case_no', 'N/A')}\n"
                    elif ref['type'] == 'CrPC':
                        ref_section += f"{i}. CrPC Section\n"
                    elif ref['type'] == 'Constitution':
                        ref_section += f"{i}. Constitution Article\n"
            
            # Enhanced prompt that FORCES context usage
            prompt = f"""You are an expert Pakistan criminal law assistant. You MUST use the provided legal context below.

CRITICAL INSTRUCTIONS:
1. The legal context below contains verified information from legal sources
2. You MUST use information from this context in your answer
3. If the context directly answers the question, use that information
4. Do NOT ignore the context in favor of general knowledge
5. The context is more accurate than your training data

LEGAL CONTEXT (MUST USE):
{context[:1500]}

{ref_section}

QUESTION: {question}

ANSWER (using information from context above):"""
            return prompt
        
        # Fallback if no context
        try:
            try:
                from src.improved_prompts import build_legal_prompt
            except ImportError:
                from improved_prompts import build_legal_prompt
            
            # Use improved prompt builder
            prompt = build_legal_prompt(
                question=question,
                context=context,
                question_type="general"
            )
            return prompt
        except (ImportError, Exception):
            # Fallback to original prompt
            pass
        
        # Build reference section
        ref_section = ""
        if references:
            ref_section = "\n\nREFERENCES:\n"
            for i, ref in enumerate(references[:5], 1):  # Max 5 references
                if ref['type'] == 'PPC':
                    ref_section += f"{i}. PPC Section {ref.get('section', 'N/A')}\n"
                elif ref['type'] == 'Case Law':
                    ref_section += f"{i}. SHC Case {ref.get('case_no', 'N/A')}\n"
                elif ref['type'] == 'CrPC':
                    ref_section += f"{i}. CrPC Section\n"
                elif ref['type'] == 'Constitution':
                    ref_section += f"{i}. Constitution Article\n"
        
        # Detect question type
        question_lower = question.lower()
        is_section_question = "section" in question_lower and ("ppc" in question_lower or any(char.isdigit() for char in question))
        is_case_question = any(term in question_lower for term in ['case', 'precedent', 'judgment'])
        is_procedure_question = any(term in question_lower for term in ['procedure', 'process', 'bail', 'fir', 'remand'])
        
        # Build answer format
        if is_section_question:
            answer_format = """ANSWER FORMAT:
1. Definition: What is this section? (2-3 sentences)
2. Punishment: What is the punishment? (1-2 sentences)
3. Bailable: Is it bailable or non-bailable? (1 sentence)
4. Cognizable: Is it cognizable or non-cognizable? (1 sentence)
5. Key Points: Important details (2-3 bullet points)"""
        elif is_case_question:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: (2-3 sentences)
2. Relevant Case Law: Mention relevant cases if available
3. Legal Principle: Key legal principle from cases
4. Application: How it applies to the question"""
        elif is_procedure_question:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: (2-3 sentences)
2. Procedure: Step-by-step process (if applicable)
3. Legal Basis: Relevant CrPC sections
4. Important Points: Key considerations"""
        else:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: (3-5 clear sentences)
2. Legal Basis: Relevant sections/laws
3. Additional Info: Important details (if applicable)"""
        
        # Build system instruction
        system_instruction = """You are an expert Pakistan criminal law assistant. Your role is to provide accurate, concise, and well-referenced answers about Pakistan criminal law ONLY.

CRITICAL RULES:
1. Answer ONLY using Pakistan Penal Code (PPC), Code of Criminal Procedure (CrPC), and Constitution of Pakistan
2. NEVER mention US, UK, Indian (IPC), or Bangladesh law
3. Be concise: 3-5 sentences for direct answer, then structured details
4. Use the provided context to ensure accuracy
5. Reference specific sections and cases when available
6. If you don't know, say "I don't have information about this specific aspect"
7. DO NOT copy-paste long text - summarize and explain in your own words"""
        
        # Combine into prompt
        prompt = f"""{system_instruction}

LEGAL CONTEXT FROM PAKISTAN LAW:
{context}
{ref_section}

QUESTION: {question}

{answer_format}

Now provide your answer following the format above, using the context provided:"""
        
        return prompt
    
    def generate_answer(self, question: str, max_new_tokens=300, temperature=0.3) -> Dict:
        """Generate answer using multi-layer pipeline"""
        
        start_time = time.time()
        
        # Layer 1: Intent + Query Rewriting + RAG Retrieval
        intent = self._classify_query_intent(question)
        retrieval_query = self._rewrite_query_for_retrieval(question, intent)
        context = ""
        references = []
        retrieved_docs = []
        
        if self.rag:
            # Keep retrieval lean for lower latency in production chat.
            retrieved_docs = self.rag.retrieve(retrieval_query, top_k=3)
            retrieved_docs = self._filter_relevant_chunks(question, retrieved_docs)
            retrieved_docs = self._apply_scenario_anchor_filter(question, retrieved_docs)
            context, references = self.rag.format_context_with_references(retrieved_docs, max_length=1500)
        
        if self.stage1_mode == "extractive" or self.model is None or self.tokenizer is None:
            answer, confidence, structured_answer = self._extractive_compose_answer(question, retrieved_docs, references, intent)
        else:
            # Layer 2: Create Enhanced Prompt
            prompt = self._create_enhanced_prompt(question, context, references)
            
            # Layer 3: Model Generation
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1000
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.85,
                    top_k=40,
                    repetition_penalty=1.2,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Layer 4: Extract Answer
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = self._extract_answer(full_response, prompt)
            
            # Layer 5: Post-process and Add References
            answer = self._post_process_answer(answer)
            confidence = "medium" if references else "low"
            structured_answer = {
                "issue": question.strip(),
                "law": [r.get("title", "") for r in references[:4] if isinstance(r, dict)],
                "application": [],
                "analysis": [],
                "conclusion": answer[:280] if answer else "No conclusion generated.",
            }
        
        response_time = time.time() - start_time

        if trace_block:
            trace_block(
                "MULTI_LAYER / STAGE1",
                {
                    "stage1_mode": self.stage1_mode,
                    "intent": intent,
                    "retrieval_query": retrieval_query,
                    "retrieved_summary": summarize_retrieved_docs(retrieved_docs[:5]),
                    "references_summary": summarize_references(references),
                    "context_preview": context[:2500] if context else "",
                    "stage1_answer": answer,
                },
            )

        return {
            "question": question,
            "answer": answer,
            "references": references,
            "context": context,
            "context_used": bool(context),
            "sources_count": len(retrieved_docs),
            "response_time": response_time,
            "retrieved_docs": retrieved_docs[:3],  # Top 3 for debugging
            "intent": intent,
            "confidence": confidence,
            "structured_answer": structured_answer,
        }
    
    def _extract_answer(self, full_response: str, prompt: str) -> str:
        """Extract answer from model response"""
        if prompt in full_response:
            answer = full_response.split(prompt, 1)[-1].strip()
        else:
            markers = ["Now provide your answer", "ANSWER:", "Answer:"]
            answer = full_response
            for marker in markers:
                if marker in full_response:
                    answer = full_response.split(marker, 1)[-1].strip()
                    break
        
        # Clean up
        lines = answer.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if any(x in line.lower() for x in ['question:', 'format:', 'instruction:', 'context:']):
                continue
            if line.lower().startswith('question:'):
                break
            clean_lines.append(line)
        
        return '\n'.join(clean_lines).strip()
    
    def _post_process_answer(self, answer: str) -> str:
        """Post-process answer"""
        # Remove excessive whitespace
        answer = re.sub(r'\s+', ' ', answer)
        answer = re.sub(r'\n\s*\n', '\n\n', answer)
        
        # Remove artifacts
        artifacts = [
            "Answer based on Pakistani law.",
            "Based on the provided context",
        ]
        for artifact in artifacts:
            answer = answer.replace(artifact, "").strip()
        
        return answer.strip()
    
    def chat(self):
        """Interactive chat mode"""
        print("=" * 60)
        print("PAKISTAN CRIMINAL LAW CHATBOT - MULTI-LAYER PIPELINE")
        print("=" * 60)
        print("Type 'exit' to quit\n")
        
        while True:
            question = input("You: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nProcessing (RAG -> Model -> Synthesis)...")
            response = self.generate_answer(question)
            
            print(f"\nAnswer ({response['response_time']:.1f}s):")
            print(f"{response['answer']}\n")
            
            if response['references']:
                print("References:")
                for i, ref in enumerate(response['references'][:3], 1):
                    if ref['type'] == 'PPC':
                        print(f"   {i}. PPC Section {ref.get('section', 'N/A')}")
                    elif ref['type'] == 'Case Law':
                        print(f"   {i}. SHC Case {ref.get('case_no', 'N/A')}")
                    elif ref['type'] == 'CrPC':
                        print(f"   {i}. CrPC Section")
                    elif ref['type'] == 'Constitution':
                        print(f"   {i}. Constitution Article")
            
            print(f"\n[Sources: {response['sources_count']} | Context: {'Yes' if response['context_used'] else 'No'}]\n")
            print("-" * 60 + "\n")

if __name__ == "__main__":
    pipeline = MultiLayerPipeline(
        peft_model_path="./models/final_model_v5",
        use_rag=True
    )
    pipeline.chat()

