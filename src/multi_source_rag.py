"""
Multi-Source RAG System for Pakistan Criminal Law
Retrieves from PPC, SHC cases, CrPC, and Constitution with weighted scoring
"""
import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict, Tuple
import re
import os
import pickle
from pathlib import Path

class MultiSourceRAG:
    """Multi-source RAG with weighted retrieval from different sources"""
    
    def __init__(self, 
                 ppc_path="./data/processed/ppc_sections.json",
                 shc_path="./data/processed/shc_cases_rag.json",
                 crpc_path="./data/processed/crpc_sections.json",
                 constitution_path="./data/processed/constitution_articles.json",
                 structured_path="./data/processed/structured_data_rag.json",
                 statute_guide_path="./pakistan_criminal_law_dataset (1).json",
                 embeddings_dir="./data/embeddings"):
        
        self.ppc_path = ppc_path
        self.shc_path = shc_path
        self.crpc_path = crpc_path
        self.constitution_path = constitution_path
        self.structured_path = structured_path  # NEW
        self.statute_guide_path = statute_guide_path
        self.embeddings_dir = embeddings_dir
        os.makedirs(embeddings_dir, exist_ok=True)
        # CPU-safe startup mode: avoid expensive fresh embedding builds on laptops.
        # Set RAG_ALLOW_CPU_EMBED_BUILD=1 to force rebuilding on CPU when needed.
        self.allow_cpu_embed_build = str(os.getenv("RAG_ALLOW_CPU_EMBED_BUILD", "0")).lower() in {"1", "true", "yes"}
        
        # Load embedding model
        print("Loading embedding model...")
        self.embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        if torch.cuda.is_available():
            self.embed_model = self.embed_model.to('cuda')
        
        # Data stores
        self.ppc_corpus = []
        self.shc_corpus = []
        self.crpc_corpus = []
        self.constitution_corpus = []
        self.structured_corpus = []  # NEW: Structured data (principles, Q&A, etc.)
        self.statute_guide_corpus = []  # Authoritative section scope dataset
        
        # Embeddings
        self.ppc_embeddings = None
        self.shc_embeddings = None
        self.crpc_embeddings = None
        self.constitution_embeddings = None
        self.structured_embeddings = None  # NEW
        self.statute_guide_embeddings = None
        
        # Load all corpora
        self._load_all_corpora()
        
        # Load or create embeddings (with caching)
        self._load_or_create_embeddings()
    
    def _load_all_corpora(self):
        """Load all corpus files"""
        print("Loading multi-source corpora...")
        
        # Load PPC
        if os.path.exists(self.ppc_path):
            with open(self.ppc_path, 'r', encoding='utf-8') as f:
                self.ppc_corpus = json.load(f)
            print(f"   PPC: {len(self.ppc_corpus)} sections")
        else:
            print(f"   WARNING: PPC not found: {self.ppc_path}")
            print(f"      Run: python process_ppc_pdf_to_json.py")
        
        # Load SHC cases
        if os.path.exists(self.shc_path):
            with open(self.shc_path, 'r', encoding='utf-8') as f:
                self.shc_corpus = json.load(f)
            print(f"   SHC Cases: {len(self.shc_corpus)} documents")
        else:
            print(f"   WARNING: SHC cases not found: {self.shc_path}")
            print(f"      Run: python process_shc_cases_to_rag.py")
        
        # Load CrPC (if exists)
        if os.path.exists(self.crpc_path):
            with open(self.crpc_path, 'r', encoding='utf-8') as f:
                self.crpc_corpus = json.load(f)
            print(f"   CrPC: {len(self.crpc_corpus)} sections")
        else:
            print(f"   WARNING: CrPC not found: {self.crpc_path}")
            print(f"      Run: python create_crpc_constitution_json.py")
        
        # Load Constitution (if exists)
        if os.path.exists(self.constitution_path):
            with open(self.constitution_path, 'r', encoding='utf-8') as f:
                self.constitution_corpus = json.load(f)
            print(f"   Constitution: {len(self.constitution_corpus)} articles")
        else:
            print(f"   WARNING: Constitution not found: {self.constitution_path}")
            print(f"      Run: python create_crpc_constitution_json.py")
        
        # Load Structured Data (principles, Q&A, evidence priority, etc.) - NEW
        if os.path.exists(self.structured_path):
            with open(self.structured_path, 'r', encoding='utf-8') as f:
                self.structured_corpus = json.load(f)
            print(f"   Structured Data: {len(self.structured_corpus)} documents (principles, Q&A, evidence priority)")
        else:
            print(f"   WARNING: Structured data not found: {self.structured_path}")
            print(f"      Run: python process_structured_data_to_rag.py")

        # Load statute guide dataset (authoritative section scope, plain language)
        if os.path.exists(self.statute_guide_path):
            try:
                with open(self.statute_guide_path, "r", encoding="utf-8") as f:
                    raw_statutes = json.load(f)
                for row in raw_statutes:
                    law_type = str(row.get("law_type", "")).strip().upper()
                    section = str(row.get("section", "")).strip()
                    title = str(row.get("title", "")).strip()
                    chapter = str(row.get("chapter", "")).strip()
                    full_text = str(row.get("full_text", "")).strip()
                    plain = str(row.get("plain_language", "")).strip()
                    scope = str(row.get("legal_scope", "")).strip()
                    use_rag = str(row.get("use_in_ai_rag", "")).strip()

                    # Compose text with strong scope signals for retrieval/reranking.
                    text = (
                        f"{law_type} Section {section}: {title}. "
                        f"Chapter: {chapter}. "
                        f"Full Text: {full_text} "
                        f"Plain Language: {plain} "
                        f"Legal Scope: {scope} "
                        f"AI Use: {use_rag}"
                    ).strip()
                    self.statute_guide_corpus.append({
                        "text": text,
                        "source": "pakistan_criminal_law_dataset",
                        "title": f"{law_type} Section {section} - {title}",
                        "metadata": {
                            "law_type": law_type.lower(),
                            "section_number": section.lower(),
                            "chapter": chapter,
                            "legal_scope": scope,
                        },
                    })
                print(f"   Statute Guide: {len(self.statute_guide_corpus)} sections")
            except Exception as e:
                print(f"   WARNING: Failed to load statute guide dataset: {e}")
        else:
            print(f"   WARNING: Statute guide not found: {self.statute_guide_path}")
        
        print(
            "Total documents loaded: "
            f"{len(self.ppc_corpus) + len(self.shc_corpus) + len(self.crpc_corpus) + len(self.constitution_corpus) + len(self.structured_corpus) + len(self.statute_guide_corpus)}"
        )
    
    def _get_embedding_path(self, source_name: str) -> str:
        """Get path for cached embeddings"""
        return os.path.join(self.embeddings_dir, f"multisource_{source_name}_embeddings.pkl")
    
    def _load_or_create_embeddings(self, force_rebuild: bool = False):
        """Load cached embeddings or create new ones"""
        print("\nLoading embeddings...")
        cpu_no_build_mode = (not torch.cuda.is_available()) and (not self.allow_cpu_embed_build) and (not force_rebuild)
        if cpu_no_build_mode:
            print("   CPU-only mode detected: skipping new embedding builds (set RAG_ALLOW_CPU_EMBED_BUILD=1 to enable).")

        def _should_build(source_label: str, corpus_size: int) -> bool:
            if not cpu_no_build_mode:
                return True
            print(
                f"   ⚠️  Skipping {source_label} embedding build on CPU ({corpus_size} docs). "
                "Using cached embeddings only."
            )
            return False
        
        # PPC embeddings
        if self.ppc_corpus:
            ppc_path = self._get_embedding_path("ppc")
            if os.path.exists(ppc_path) and not force_rebuild:
                try:
                    print("   Loading cached PPC embeddings...")
                    with open(ppc_path, 'rb') as f:
                        self.ppc_embeddings = pickle.load(f)
                    # Move to GPU if available
                    if torch.cuda.is_available() and isinstance(self.ppc_embeddings, torch.Tensor):
                        self.ppc_embeddings = self.ppc_embeddings.to('cuda')
                    print(f"   ✅ Loaded PPC embeddings ({len(self.ppc_corpus)} documents)")
                except Exception as e:
                    print(f"   ⚠️  Failed to load cached PPC embeddings: {e}")
                    if _should_build("PPC", len(self.ppc_corpus)):
                        print("   Creating new PPC embeddings...")
                        self._create_ppc_embeddings()
            else:
                if _should_build("PPC", len(self.ppc_corpus)):
                    print("   Creating PPC embeddings...")
                    self._create_ppc_embeddings()
        
        # SHC embeddings
        if self.shc_corpus:
            shc_path = self._get_embedding_path("shc")
            if os.path.exists(shc_path) and not force_rebuild:
                try:
                    print("   Loading cached SHC embeddings...")
                    with open(shc_path, 'rb') as f:
                        self.shc_embeddings = pickle.load(f)
                    # Move to GPU if available
                    if torch.cuda.is_available() and isinstance(self.shc_embeddings, torch.Tensor):
                        self.shc_embeddings = self.shc_embeddings.to('cuda')
                    print(f"   ✅ Loaded SHC embeddings ({len(self.shc_corpus)} documents)")
                except Exception as e:
                    print(f"   ⚠️  Failed to load cached SHC embeddings: {e}")
                    if _should_build("SHC", len(self.shc_corpus)):
                        print("   Creating new SHC embeddings...")
                        self._create_shc_embeddings()
            else:
                if _should_build("SHC", len(self.shc_corpus)):
                    print("   Creating SHC embeddings...")
                    self._create_shc_embeddings()
        
        # CrPC embeddings
        if self.crpc_corpus:
            crpc_path = self._get_embedding_path("crpc")
            if os.path.exists(crpc_path) and not force_rebuild:
                try:
                    print("   Loading cached CrPC embeddings...")
                    with open(crpc_path, 'rb') as f:
                        self.crpc_embeddings = pickle.load(f)
                    # Move to GPU if available
                    if torch.cuda.is_available() and isinstance(self.crpc_embeddings, torch.Tensor):
                        self.crpc_embeddings = self.crpc_embeddings.to('cuda')
                    print(f"   ✅ Loaded CrPC embeddings ({len(self.crpc_corpus)} documents)")
                except Exception as e:
                    print(f"   ⚠️  Failed to load cached CrPC embeddings: {e}")
                    if _should_build("CrPC", len(self.crpc_corpus)):
                        print("   Creating new CrPC embeddings...")
                        self._create_crpc_embeddings()
            else:
                if _should_build("CrPC", len(self.crpc_corpus)):
                    print("   Creating CrPC embeddings...")
                    self._create_crpc_embeddings()
        
        # Constitution embeddings
        if self.constitution_corpus:
            const_path = self._get_embedding_path("constitution")
            if os.path.exists(const_path) and not force_rebuild:
                try:
                    print("   Loading cached Constitution embeddings...")
                    with open(const_path, 'rb') as f:
                        self.constitution_embeddings = pickle.load(f)
                    # Move to GPU if available
                    if torch.cuda.is_available() and isinstance(self.constitution_embeddings, torch.Tensor):
                        self.constitution_embeddings = self.constitution_embeddings.to('cuda')
                    print(f"   ✅ Loaded Constitution embeddings ({len(self.constitution_corpus)} documents)")
                except Exception as e:
                    print(f"   ⚠️  Failed to load cached Constitution embeddings: {e}")
                    if _should_build("Constitution", len(self.constitution_corpus)):
                        print("   Creating new Constitution embeddings...")
                        self._create_constitution_embeddings()
            else:
                if _should_build("Constitution", len(self.constitution_corpus)):
                    print("   Creating Constitution embeddings...")
                    self._create_constitution_embeddings()
        
        # Structured data embeddings
        if self.structured_corpus:
            structured_path = self._get_embedding_path("structured")
            if os.path.exists(structured_path) and not force_rebuild:
                try:
                    print("   Loading cached Structured data embeddings...")
                    with open(structured_path, 'rb') as f:
                        self.structured_embeddings = pickle.load(f)
                    # Move to GPU if available
                    if torch.cuda.is_available() and isinstance(self.structured_embeddings, torch.Tensor):
                        self.structured_embeddings = self.structured_embeddings.to('cuda')
                    print(f"   ✅ Loaded Structured data embeddings ({len(self.structured_corpus)} documents)")
                except Exception as e:
                    print(f"   ⚠️  Failed to load cached Structured data embeddings: {e}")
                    if _should_build("Structured data", len(self.structured_corpus)):
                        print("   Creating new Structured data embeddings...")
                        self._create_structured_embeddings()
            else:
                if _should_build("Structured data", len(self.structured_corpus)):
                    print("   Creating Structured data embeddings...")
                    self._create_structured_embeddings()

        # Statute guide embeddings
        if self.statute_guide_corpus:
            statute_path = self._get_embedding_path("statute_guide")
            if os.path.exists(statute_path) and not force_rebuild:
                try:
                    print("   Loading cached Statute Guide embeddings...")
                    with open(statute_path, "rb") as f:
                        self.statute_guide_embeddings = pickle.load(f)
                    if torch.cuda.is_available() and isinstance(self.statute_guide_embeddings, torch.Tensor):
                        self.statute_guide_embeddings = self.statute_guide_embeddings.to("cuda")
                    print(f"   ✅ Loaded Statute Guide embeddings ({len(self.statute_guide_corpus)} documents)")
                except Exception as e:
                    print(f"   ⚠️  Failed to load cached Statute Guide embeddings: {e}")
                    if _should_build("Statute Guide", len(self.statute_guide_corpus)):
                        print("   Creating new Statute Guide embeddings...")
                        self._create_statute_guide_embeddings()
            else:
                if _should_build("Statute Guide", len(self.statute_guide_corpus)):
                    print("   Creating Statute Guide embeddings...")
                    self._create_statute_guide_embeddings()
    
    def _create_ppc_embeddings(self):
        """Create and save PPC embeddings"""
        ppc_texts = [doc.get('text', '') for doc in self.ppc_corpus]
        self.ppc_embeddings = self.embed_model.encode(ppc_texts, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
        # Save to cache
        ppc_path = self._get_embedding_path("ppc")
        with open(ppc_path, 'wb') as f:
            pickle.dump(self.ppc_embeddings.cpu(), f)  # Save CPU tensor
        self.ppc_embeddings = self.ppc_embeddings.to('cuda') if torch.cuda.is_available() else self.ppc_embeddings
        print(f"   ✅ PPC embeddings created and saved")
    
    def _create_shc_embeddings(self):
        """Create and save SHC embeddings"""
        shc_texts = [doc.get('text', '') for doc in self.shc_corpus]
        self.shc_embeddings = self.embed_model.encode(shc_texts, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
        # Save to cache
        shc_path = self._get_embedding_path("shc")
        with open(shc_path, 'wb') as f:
            pickle.dump(self.shc_embeddings.cpu(), f)  # Save CPU tensor
        self.shc_embeddings = self.shc_embeddings.to('cuda') if torch.cuda.is_available() else self.shc_embeddings
        print(f"   ✅ SHC embeddings created and saved")
    
    def _create_crpc_embeddings(self):
        """Create and save CrPC embeddings"""
        crpc_texts = [doc.get('text', '') for doc in self.crpc_corpus]
        self.crpc_embeddings = self.embed_model.encode(crpc_texts, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
        # Save to cache
        crpc_path = self._get_embedding_path("crpc")
        with open(crpc_path, 'wb') as f:
            pickle.dump(self.crpc_embeddings.cpu(), f)  # Save CPU tensor
        self.crpc_embeddings = self.crpc_embeddings.to('cuda') if torch.cuda.is_available() else self.crpc_embeddings
        print(f"   ✅ CrPC embeddings created and saved")
    
    def _create_constitution_embeddings(self):
        """Create and save Constitution embeddings"""
        const_texts = [doc.get('text', '') for doc in self.constitution_corpus]
        self.constitution_embeddings = self.embed_model.encode(const_texts, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
        # Save to cache
        const_path = self._get_embedding_path("constitution")
        with open(const_path, 'wb') as f:
            pickle.dump(self.constitution_embeddings.cpu(), f)  # Save CPU tensor
        self.constitution_embeddings = self.constitution_embeddings.to('cuda') if torch.cuda.is_available() else self.constitution_embeddings
        print(f"   ✅ Constitution embeddings created and saved")
    
    def _create_structured_embeddings(self):
        """Create and save Structured data embeddings"""
        structured_texts = [doc.get('text', '') for doc in self.structured_corpus]
        self.structured_embeddings = self.embed_model.encode(structured_texts, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
        # Save to cache
        structured_path = self._get_embedding_path("structured")
        with open(structured_path, 'wb') as f:
            pickle.dump(self.structured_embeddings.cpu(), f)  # Save CPU tensor
        self.structured_embeddings = self.structured_embeddings.to('cuda') if torch.cuda.is_available() else self.structured_embeddings
        print(f"   ✅ Structured data embeddings created and saved")

    def _create_statute_guide_embeddings(self):
        """Create and save statute guide embeddings."""
        statute_texts = [doc.get("text", "") for doc in self.statute_guide_corpus]
        self.statute_guide_embeddings = self.embed_model.encode(
            statute_texts,
            convert_to_tensor=True,
            show_progress_bar=True,
            batch_size=32,
        )
        statute_path = self._get_embedding_path("statute_guide")
        with open(statute_path, "wb") as f:
            pickle.dump(self.statute_guide_embeddings.cpu(), f)
        self.statute_guide_embeddings = self.statute_guide_embeddings.to("cuda") if torch.cuda.is_available() else self.statute_guide_embeddings
        print("   ✅ Statute Guide embeddings created and saved")
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related terms for better retrieval"""
        query_lower = query.lower()
        expanded_terms = []
        
        # Add original query
        expanded_terms.append(query)
        
        # Expand compromise/family wishes scenarios
        if any(term in query_lower for term in ['family', 'doesn\'t want', 'don\'t want', 'no punishment', 'compromise']):
            expanded_terms.append('compromise criminal case family wishes')
            expanded_terms.append('diyat blood money qatl-i-amd')
            expanded_terms.append('section 345 CrPC compounding offences')
            expanded_terms.append('legal heirs compromise murder case')
        
        # Expand fight/death scenarios
        if any(term in query_lower for term in ['fight', 'dies', 'death', 'killed']):
            expanded_terms.append('qatl-i-amd murder intentional killing')
            expanded_terms.append('section 302 PPC punishment')
            expanded_terms.append('homicide criminal liability')
        
        # Expand private-defence / robbery scenarios (critical criminal-law mapping)
        if any(term in query_lower for term in ['self defence', 'self-defense', 'private defence', 'private defense', 'robbery', 'robber', 'shopkeeper']):
            expanded_terms.append('right of private defence ppc sections 96 97 99 100 101 102 103 104 106')
            expanded_terms.append('murder vs lawful self defence immediate threat proportional force')
            expanded_terms.append('armed robbery defensive killing legal justification pakistan')

        # Expand juvenile/child-offender comparison scenarios.
        if any(term in query_lower for term in ['juvenile', 'child', 'minor', 'under 18', 'teen', 'jjsa', 'juvenile justice']):
            expanded_terms.append('Juvenile Justice System Act Pakistan child offender age determination')
            expanded_terms.append('juvenile court borstal institution probation rehabilitation privacy')
            expanded_terms.append('juvenile vs adult criminal law punishment bail trial differences')

        # Expand unlawful assembly / highway blockade protest scenarios.
        if any(term in query_lower for term in ['protest', 'rally', 'assembly', 'block', 'blocked', 'highway', 'road']):
            expanded_terms.append('unlawful assembly riot common object ppc sections 141 146 147 149')
            expanded_terms.append('obstruction of public way ppc section 283 wrongful restraint')
            expanded_terms.append('crpc preventive powers public order dispersal')

        # Expand public-servant bribery / corruption scenarios.
        if any(term in query_lower for term in ['government officer', 'public servant', 'bribe', 'illegal gratification', 'corruption', 'license approval']):
            expanded_terms.append('public servant illegal gratification anti-corruption law pakistan')
            expanded_terms.append('prevention of corruption criminal misconduct extortion ppc')
            expanded_terms.append('demand for money for official act offence framework')
        
        # Expand bail questions
        if 'bail' in query_lower:
            expanded_terms.append('section 497 CrPC bail non-bailable')
            expanded_terms.append('bail application procedure')
        
        # Expand FIR questions
        if 'fir' in query_lower or 'first information' in query_lower:
            expanded_terms.append('section 154 CrPC FIR filing')
            expanded_terms.append('cognizable offence information report')
        
        # Expand evidence questions
        if any(term in query_lower for term in ['evidence', 'witness', 'medical', 'ocular']):
            expanded_terms.append('evidence priority ocular medical')
            expanded_terms.append('witness credibility material contradiction')
        
        # Join expanded terms
        return ' '.join(expanded_terms)
    
    def _detect_query_type(self, query: str) -> Dict[str, float]:
        """Detect query type and return weights for different sources"""
        query_lower = query.lower()
        
        weights = {
            'ppc': 1.0,
            'shc': 1.0,
            'crpc': 1.0,
            'constitution': 1.0,
            'structured': 1.0,  # NEW: Structured data (principles, Q&A, evidence priority)
            'statute_guide': 1.0,
        }
        
        # Section question - prioritize PPC
        if re.search(r'section\s+\d+[A-Z]?\s+ppc', query_lower):
            weights['ppc'] = 2.0
            weights['statute_guide'] = 3.0
            weights['shc'] = 1.5  # Cases mentioning this section
            weights['crpc'] = 0.5
        
        # CrPC question - prioritize CrPC
        elif re.search(r'section\s+\d+[A-Z]?\s+crpc|cr\.p\.c', query_lower):
            weights['crpc'] = 2.0
            weights['statute_guide'] = 3.0
            weights['ppc'] = 0.5
        
        # Private defence / robbery / killing scenarios: prioritize penal-code core.
        elif any(term in query_lower for term in [
            'private defence', 'private defense', 'self defence', 'self-defense', 'self defense',
            'robbery', 'robber', 'dacoity', 'shopkeeper', 'killed', 'killing', 'culpable homicide'
        ]):
            weights['ppc'] = 3.2
            weights['statute_guide'] = 3.4
            weights['structured'] = 1.3
            weights['shc'] = 0.55
            weights['crpc'] = 0.8
            weights['constitution'] = 0.25

        # Juvenile/child-offender treatment comparison.
        elif any(term in query_lower for term in [
            'juvenile', 'child offender', 'minor', 'under 18', 'teen', 'jjsa', 'juvenile justice'
        ]):
            weights['statute_guide'] = 3.4
            weights['structured'] = 2.4
            weights['ppc'] = 1.6
            weights['crpc'] = 1.1
            weights['shc'] = 0.7
            weights['constitution'] = 0.5

        # Unlawful assembly / highway blockade protest scenarios.
        elif any(term in query_lower for term in [
            'protest', 'unlawful assembly', 'assembly', 'highway', 'blocked road', 'public way', 'riot'
        ]):
            weights['ppc'] = 3.0
            weights['statute_guide'] = 3.2
            weights['crpc'] = 1.4
            weights['structured'] = 1.5
            weights['shc'] = 0.6
            weights['constitution'] = 0.4

        # Public servant bribery / anti-corruption scenarios.
        elif any(term in query_lower for term in [
            'public servant', 'government officer', 'bribe', 'illegal gratification', 'corruption', 'license approval'
        ]):
            weights['statute_guide'] = 3.2
            weights['structured'] = 2.2
            weights['ppc'] = 1.8
            weights['crpc'] = 1.0
            weights['shc'] = 0.6
            weights['constitution'] = 0.3

        # Case law question - prioritize SHC
        elif any(term in query_lower for term in ['case', 'precedent', 'judgment', 'court decision']):
            weights['shc'] = 2.0
            weights['ppc'] = 1.0
        
        # Rights question - prioritize Constitution (unless clearly criminal self-defence context)
        elif any(term in query_lower for term in ['right', 'article', 'constitution', 'fundamental']) and not any(
            term in query_lower for term in ['private defence', 'self defence', 'self-defense', 'murder', 'robbery', 'killing']
        ):
            weights['constitution'] = 2.0
            weights['crpc'] = 1.5
        
        # Bail question - prioritize CrPC and cases
        elif 'bail' in query_lower:
            weights['crpc'] = 2.0
            weights['shc'] = 1.5
            weights['ppc'] = 0.8
        
        # Procedure question - prioritize CrPC
        elif any(term in query_lower for term in ['procedure', 'process', 'fir', 'remand', 'investigation']):
            weights['crpc'] = 2.0
            weights['statute_guide'] = 2.5
            weights['shc'] = 1.0
        
        # Evidence/Principle question - prioritize Structured data (NEW)
        elif any(term in query_lower for term in ['evidence', 'priority', 'primacy', 'principle', 'rule', 'eyewitness', 'ocular', 'medical evidence']):
            weights['structured'] = 3.0  # High priority for evidence questions
            weights['shc'] = 1.5  # Cases may also have relevant info
            weights['ppc'] = 1.0
        
        return weights

    def _extract_query_tokens(self, query: str) -> set:
        """Extract useful lexical tokens for hybrid reranking."""
        stopwords = {
            "the", "and", "for", "with", "from", "that", "this", "what", "when", "where",
            "which", "about", "into", "after", "before", "should", "would", "could", "have",
            "has", "had", "your", "their", "there", "them", "they", "how", "can", "under",
            "against", "case", "law", "pakistan"
        }
        tokens = re.findall(r"[a-zA-Z0-9]+", query.lower())
        return {t for t in tokens if len(t) >= 3 and t not in stopwords}

    def _extract_section_targets(self, query: str) -> Dict[str, set]:
        """Detect explicit section references in the query."""
        lower_query = query.lower()
        ppc_sections = set(re.findall(r"section\s+(\d+[a-z]?)\s+ppc", lower_query))
        crpc_sections = set(re.findall(r"section\s+(\d+[a-z]?)\s+crpc", lower_query))
        return {"ppc": ppc_sections, "crpc": crpc_sections}

    def _extract_section_from_doc(self, doc: Dict) -> str:
        """Best-effort extraction of section number from heterogeneous corpus docs."""
        metadata = doc.get("metadata", {}) or {}
        for key in ["section_number", "section", "section_no"]:
            val = str(metadata.get(key, "")).strip()
            if val:
                return val.lower()
        for key in ["section", "section_number"]:
            val = str(doc.get(key, "")).strip()
            if val:
                return val.lower()
        title = str(doc.get("title", "")).lower()
        m = re.search(r"section\s+(\d+[a-z]?)", title)
        return m.group(1).lower() if m else ""

    def _build_section_anchor_results(self, section_targets: Dict[str, set]) -> List[Dict]:
        """
        Force-anchor exact section matches so targeted statute queries cannot drift.
        These results get very high scores and are inserted first.
        """
        anchors: List[Dict] = []

        def append_anchor(doc: Dict, law_code: str, source_type: str):
            section_no = self._extract_section_from_doc(doc)
            title = doc.get("title", f"{law_code.upper()} Section {section_no}")
            text = doc.get("text", "")
            metadata = (doc.get("metadata", {}) or {}).copy()
            metadata["section_number"] = section_no
            metadata["law_type"] = law_code
            anchors.append({
                "text": text,
                "score": 999.0,  # hard priority anchor
                "semantic_score": 1.0,
                "lexical_score": 1.0,
                "source": doc.get("source", source_type),
                "type": source_type,
                "title": title,
                "metadata": metadata,
            })

        # Prefer authoritative statute guide first.
        if self.statute_guide_corpus:
            for doc in self.statute_guide_corpus:
                sec = self._extract_section_from_doc(doc)
                law = str((doc.get("metadata", {}) or {}).get("law_type", "")).lower()
                if sec and sec in section_targets["crpc"] and law == "crpc":
                    append_anchor(doc, "crpc", "statute_guide")
                if sec and sec in section_targets["ppc"] and law == "ppc":
                    append_anchor(doc, "ppc", "statute_guide")

        # Fallback to base corpora exact matches.
        for doc in self.crpc_corpus:
            sec = self._extract_section_from_doc(doc)
            if sec and sec in section_targets["crpc"]:
                append_anchor(doc, "crpc", "crpc")
        for doc in self.ppc_corpus:
            sec = self._extract_section_from_doc(doc)
            if sec and sec in section_targets["ppc"]:
                append_anchor(doc, "ppc", "ppc")

        # Deduplicate by type + section
        unique = []
        seen = set()
        for item in anchors:
            key = (item.get("type"), str(item.get("metadata", {}).get("section_number", "")))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    def _lexical_overlap_score(self, query_tokens: set, text: str, title: str = "") -> float:
        """Simple lexical overlap score (0..1) for semantic tie-breaking."""
        if not query_tokens:
            return 0.0
        haystack = f"{title} {text[:600]}".lower()
        hit_count = sum(1 for token in query_tokens if token in haystack)
        return hit_count / max(1, len(query_tokens))

    def _freshness_boost(self, metadata: Dict, title: str = "") -> float:
        """
        Small boost for relatively recent case-law entries when year is available.
        Keeps impact low to avoid hurting legal relevance.
        """
        year = None
        for candidate in [str(metadata.get("year", "")), str(metadata.get("case_no", "")), title]:
            match = re.search(r"(19|20)\d{2}", candidate)
            if match:
                year = int(match.group())
                break
        if not year:
            return 0.0
        if year >= 2022:
            return 0.10
        if year >= 2018:
            return 0.06
        if year >= 2010:
            return 0.03
        return 0.0
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve using hybrid semantic+lexical scoring with source diversity."""
        
        # Expand query for better retrieval
        expanded_query = self._expand_query(query)
        
        # Detect query type
        weights = self._detect_query_type(expanded_query)
        query_tokens = self._extract_query_tokens(query)
        section_targets = self._extract_section_targets(query)
        candidate_k = max(top_k * 4, 12)
        
        # Get query embedding (use expanded query for better semantic matching)
        query_embedding = self.embed_model.encode(expanded_query, convert_to_tensor=True)
        if torch.cuda.is_available():
            query_embedding = query_embedding.to('cuda')
        
        all_results = []

        # Hard section anchor injection for targeted section queries.
        if section_targets["ppc"] or section_targets["crpc"]:
            all_results.extend(self._build_section_anchor_results(section_targets))
        
        # Retrieve from PPC
        if self.ppc_corpus and self.ppc_embeddings is not None:
            if torch.cuda.is_available():
                ppc_emb = self.ppc_embeddings.to('cuda')
            else:
                ppc_emb = self.ppc_embeddings
            
            ppc_scores = util.cos_sim(query_embedding, ppc_emb)[0]
            top_ppc = torch.topk(ppc_scores, k=min(candidate_k, len(ppc_scores)))
            for idx in top_ppc.indices:
                doc = self.ppc_corpus[idx]
                metadata = doc.get('metadata', {})
                semantic_score = float(ppc_scores[idx])
                lexical_score = self._lexical_overlap_score(query_tokens, doc.get('text', ''), doc.get('title', ''))
                section_no = str(metadata.get('section_number', '')).lower()
                section_boost = 0.15 if section_no and section_no in section_targets["ppc"] else 0.0
                final_score = (semantic_score * weights['ppc'] * 0.78) + (lexical_score * 0.22) + section_boost
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": final_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "source": doc.get('source', 'ppc'),
                    "type": "ppc",
                    "title": doc.get('title', f"PPC Section {doc.get('section_number', '')}"),
                    "metadata": metadata
                })
        
        # Retrieve from SHC cases
        if self.shc_corpus and self.shc_embeddings is not None:
            if torch.cuda.is_available():
                shc_emb = self.shc_embeddings.to('cuda')
            else:
                shc_emb = self.shc_embeddings
            
            shc_scores = util.cos_sim(query_embedding, shc_emb)[0]
            top_shc = torch.topk(shc_scores, k=min(candidate_k, len(shc_scores)))
            for idx in top_shc.indices:
                doc = self.shc_corpus[idx]
                metadata = doc.get('metadata', {})
                semantic_score = float(shc_scores[idx])
                lexical_score = self._lexical_overlap_score(query_tokens, doc.get('text', ''), doc.get('title', ''))
                freshness = self._freshness_boost(metadata, doc.get('title', ''))
                final_score = (semantic_score * weights['shc'] * 0.80) + (lexical_score * 0.20) + freshness
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": final_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "source": doc.get('source', 'shc'),
                    "type": "case_law",
                    "title": doc.get('title', 'SHC Case'),
                    "metadata": metadata
                })
        
        # Retrieve from CrPC
        if self.crpc_corpus and self.crpc_embeddings is not None:
            if torch.cuda.is_available():
                crpc_emb = self.crpc_embeddings.to('cuda')
            else:
                crpc_emb = self.crpc_embeddings
            
            crpc_scores = util.cos_sim(query_embedding, crpc_emb)[0]
            top_crpc = torch.topk(crpc_scores, k=min(candidate_k, len(crpc_scores)))
            for idx in top_crpc.indices:
                doc = self.crpc_corpus[idx]
                metadata = doc.get('metadata', {})
                semantic_score = float(crpc_scores[idx])
                lexical_score = self._lexical_overlap_score(query_tokens, doc.get('text', ''), doc.get('title', ''))
                section_no = str(metadata.get('section_number', '')).lower()
                section_boost = 0.15 if section_no and section_no in section_targets["crpc"] else 0.0
                final_score = (semantic_score * weights['crpc'] * 0.78) + (lexical_score * 0.22) + section_boost
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": final_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "source": doc.get('source', 'crpc'),
                    "type": "crpc",
                    "title": doc.get('title', 'CrPC Section'),
                    "metadata": metadata
                })
        
        # Retrieve from Constitution
        if self.constitution_corpus and self.constitution_embeddings is not None:
            if torch.cuda.is_available():
                const_emb = self.constitution_embeddings.to('cuda')
            else:
                const_emb = self.constitution_embeddings
            
            const_scores = util.cos_sim(query_embedding, const_emb)[0]
            top_const = torch.topk(const_scores, k=min(candidate_k, len(const_scores)))
            for idx in top_const.indices:
                doc = self.constitution_corpus[idx]
                semantic_score = float(const_scores[idx])
                lexical_score = self._lexical_overlap_score(query_tokens, doc.get('text', ''), doc.get('title', ''))
                final_score = (semantic_score * weights['constitution'] * 0.78) + (lexical_score * 0.22)
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": final_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "source": doc.get('source', 'constitution'),
                    "type": "constitution",
                    "title": doc.get('title', 'Constitution Article'),
                    "metadata": doc.get('metadata', {})
                })
        
        # Retrieve from Structured Data (principles, Q&A, evidence priority) - NEW
        if self.structured_corpus and self.structured_embeddings is not None:
            if torch.cuda.is_available():
                struct_emb = self.structured_embeddings.to('cuda')
            else:
                struct_emb = self.structured_embeddings
            
            struct_scores = util.cos_sim(query_embedding, struct_emb)[0]
            top_struct = torch.topk(struct_scores, k=min(candidate_k, len(struct_scores)))
            for idx in top_struct.indices:
                doc = self.structured_corpus[idx]
                semantic_score = float(struct_scores[idx])
                lexical_score = self._lexical_overlap_score(query_tokens, doc.get('text', ''), doc.get('title', ''))
                final_score = (semantic_score * weights.get('structured', 1.0) * 0.75) + (lexical_score * 0.25)
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": final_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "source": doc.get('source', 'structured_data'),
                    "type": doc.get('category', 'principle'),
                    "title": doc.get('title', doc.get('category', 'Legal Principle')),
                    "metadata": doc.get('metadata', {})
                })

        # Retrieve from statute guide corpus (authoritative section scope)
        if self.statute_guide_corpus and self.statute_guide_embeddings is not None:
            if torch.cuda.is_available():
                statute_emb = self.statute_guide_embeddings.to("cuda")
            else:
                statute_emb = self.statute_guide_embeddings

            statute_scores = util.cos_sim(query_embedding, statute_emb)[0]
            top_statute = torch.topk(statute_scores, k=min(candidate_k, len(statute_scores)))
            for idx in top_statute.indices:
                doc = self.statute_guide_corpus[idx]
                metadata = doc.get("metadata", {})
                semantic_score = float(statute_scores[idx])
                lexical_score = self._lexical_overlap_score(query_tokens, doc.get("text", ""), doc.get("title", ""))
                section_no = str(metadata.get("section_number", "")).lower()
                law_type = str(metadata.get("law_type", "")).lower()
                section_boost = 0.0
                if section_no:
                    if section_no in section_targets["ppc"] and law_type == "ppc":
                        section_boost = 0.30
                    if section_no in section_targets["crpc"] and law_type == "crpc":
                        section_boost = 0.30

                final_score = (semantic_score * weights.get("statute_guide", 1.0) * 0.72) + (lexical_score * 0.28) + section_boost
                all_results.append({
                    "text": doc.get("text", ""),
                    "score": final_score,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "source": doc.get("source", "pakistan_criminal_law_dataset"),
                    "type": "statute_guide",
                    "title": doc.get("title", "Statute Guide Section"),
                    "metadata": metadata,
                })
        
        # Sort by weighted score, then choose diverse top results.
        all_results.sort(key=lambda x: x['score'], reverse=True)
        primary_weight_key = max(weights, key=weights.get)
        primary_type_map = {
            "ppc": "ppc",
            "shc": "case_law",
            "crpc": "crpc",
            "constitution": "constitution",
            "structured": "principle",
            "statute_guide": "statute_guide",
        }
        primary_type = primary_type_map.get(primary_weight_key, "")

        primary_cap = max(2, top_k - 1)
        other_cap = max(1, top_k // 2)

        selected = []
        seen_texts = set()
        type_counts: Dict[str, int] = {}

        for item in all_results:
            item_type = item.get("type", "unknown")
            cap = primary_cap if item_type == primary_type else other_cap
            if type_counts.get(item_type, 0) >= cap:
                continue
            text_key = item.get("text", "")[:220]
            if text_key in seen_texts:
                continue
            selected.append(item)
            seen_texts.add(text_key)
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            if len(selected) >= top_k:
                break

        if len(selected) < top_k:
            for item in all_results:
                text_key = item.get("text", "")[:220]
                if text_key in seen_texts:
                    continue
                selected.append(item)
                seen_texts.add(text_key)
                if len(selected) >= top_k:
                    break

        return selected
    
    def format_context_with_references(self, retrieved_docs: List[Dict], max_length: int = 2000) -> Tuple[str, List[Dict]]:
        """Format context with proper references"""
        context_parts = []
        references = []
        
        current_length = 0
        per_doc_cap = 900
        for i, doc in enumerate(retrieved_docs):
            text = doc['text']
            source = doc['source']
            title = doc['title']
            doc_type = doc.get('type', 'unknown')
            text_for_context = text if len(text) <= per_doc_cap else (text[:per_doc_cap].rsplit(" ", 1)[0] + "...")

            # Try to include as many relevant docs as possible in context.
            if current_length + len(text_for_context) > max_length:
                remaining = max_length - current_length
                if remaining < 140:
                    continue
                text_for_context = text_for_context[:remaining].rsplit(" ", 1)[0] + "..."
            
            # Format based on type
            if doc_type == 'ppc':
                context_parts.append(f"[PPC Section {doc.get('metadata', {}).get('section_number', '')}]: {text_for_context}")
                references.append({
                    "type": "PPC",
                    "section": doc.get('metadata', {}).get('section_number', ''),
                    "title": title
                })
            elif doc_type == 'case_law':
                case_no = doc.get('metadata', {}).get('case_no', '')
                context_parts.append(f"[SHC Case {case_no}]: {text_for_context}")
                references.append({
                    "type": "Case Law",
                    "case_no": case_no,
                    "title": title,
                    "pdf_url": doc.get('metadata', {}).get('pdf_url', '')
                })
            elif doc_type == 'crpc':
                context_parts.append(f"[CrPC Section]: {text_for_context}")
                references.append({
                    "type": "CrPC",
                    "title": title
                })
            elif doc_type == 'constitution':
                context_parts.append(f"[Constitution]: {text_for_context}")
                references.append({
                    "type": "Constitution",
                    "title": title
                })
            elif doc_type == 'statute_guide':
                law_type = str(doc.get("metadata", {}).get("law_type", "")).upper()
                section_no = str(doc.get("metadata", {}).get("section_number", ""))
                context_parts.append(f"[{law_type} Section {section_no}]: {text_for_context}")
                ref_type = "Statute"
                if law_type == "PPC":
                    ref_type = "PPC"
                elif law_type == "CRPC":
                    ref_type = "CrPC"
                references.append({
                    "type": ref_type,
                    "section": section_no,
                    "title": title,
                    "legal_scope": doc.get("metadata", {}).get("legal_scope", ""),
                })
            else:
                context_parts.append(f"[{title}]: {text_for_context}")
                references.append({
                    "type": doc_type,
                    "title": title
                })
            
            current_length += len(text_for_context)
        
        context = "\n\n".join(context_parts)
        return context, references

