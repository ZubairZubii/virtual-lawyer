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
                 embeddings_dir="./data/embeddings"):
        
        self.ppc_path = ppc_path
        self.shc_path = shc_path
        self.crpc_path = crpc_path
        self.constitution_path = constitution_path
        self.structured_path = structured_path  # NEW
        self.embeddings_dir = embeddings_dir
        os.makedirs(embeddings_dir, exist_ok=True)
        
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
        
        # Embeddings
        self.ppc_embeddings = None
        self.shc_embeddings = None
        self.crpc_embeddings = None
        self.constitution_embeddings = None
        self.structured_embeddings = None  # NEW
        
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
        
        print(f"Total documents loaded: {len(self.ppc_corpus) + len(self.shc_corpus) + len(self.crpc_corpus) + len(self.constitution_corpus) + len(self.structured_corpus)}")
    
    def _get_embedding_path(self, source_name: str) -> str:
        """Get path for cached embeddings"""
        return os.path.join(self.embeddings_dir, f"multisource_{source_name}_embeddings.pkl")
    
    def _load_or_create_embeddings(self, force_rebuild: bool = False):
        """Load cached embeddings or create new ones"""
        print("\nLoading embeddings...")
        
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
                    print("   Creating new PPC embeddings...")
                    self._create_ppc_embeddings()
            else:
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
                    print("   Creating new SHC embeddings...")
                    self._create_shc_embeddings()
            else:
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
                    print("   Creating new CrPC embeddings...")
                    self._create_crpc_embeddings()
            else:
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
                    print("   Creating new Constitution embeddings...")
                    self._create_constitution_embeddings()
            else:
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
                    print("   Creating new Structured data embeddings...")
                    self._create_structured_embeddings()
            else:
                print("   Creating Structured data embeddings...")
                self._create_structured_embeddings()
    
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
            'structured': 1.0  # NEW: Structured data (principles, Q&A, evidence priority)
        }
        
        # Section question - prioritize PPC
        if re.search(r'section\s+\d+[A-Z]?\s+ppc', query_lower):
            weights['ppc'] = 2.0
            weights['shc'] = 1.5  # Cases mentioning this section
            weights['crpc'] = 0.5
        
        # CrPC question - prioritize CrPC
        elif re.search(r'section\s+\d+[A-Z]?\s+crpc|cr\.p\.c', query_lower):
            weights['crpc'] = 2.0
            weights['ppc'] = 0.5
        
        # Case law question - prioritize SHC
        elif any(term in query_lower for term in ['case', 'precedent', 'judgment', 'court decision']):
            weights['shc'] = 2.0
            weights['ppc'] = 1.0
        
        # Rights question - prioritize Constitution
        elif any(term in query_lower for term in ['right', 'article', 'constitution', 'fundamental']):
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
            weights['shc'] = 1.0
        
        # Evidence/Principle question - prioritize Structured data (NEW)
        elif any(term in query_lower for term in ['evidence', 'priority', 'primacy', 'principle', 'rule', 'eyewitness', 'ocular', 'medical evidence']):
            weights['structured'] = 3.0  # High priority for evidence questions
            weights['shc'] = 1.5  # Cases may also have relevant info
            weights['ppc'] = 1.0
        
        return weights
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve from all sources with weighted scoring and query expansion"""
        
        # Expand query for better retrieval
        expanded_query = self._expand_query(query)
        
        # Detect query type
        weights = self._detect_query_type(expanded_query)
        
        # Get query embedding (use expanded query for better semantic matching)
        query_embedding = self.embed_model.encode(expanded_query, convert_to_tensor=True)
        if torch.cuda.is_available():
            query_embedding = query_embedding.to('cuda')
        
        all_results = []
        
        # Retrieve from PPC
        if self.ppc_corpus and self.ppc_embeddings is not None:
            if torch.cuda.is_available():
                ppc_emb = self.ppc_embeddings.to('cuda')
            else:
                ppc_emb = self.ppc_embeddings
            
            ppc_scores = util.cos_sim(query_embedding, ppc_emb)[0]
            top_ppc = torch.topk(ppc_scores, k=min(top_k, len(ppc_scores)))
            for idx in top_ppc.indices:
                doc = self.ppc_corpus[idx]
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": float(ppc_scores[idx] * weights['ppc']),
                    "source": doc.get('source', 'ppc'),
                    "type": "ppc",
                    "title": doc.get('title', f"PPC Section {doc.get('section_number', '')}"),
                    "metadata": doc.get('metadata', {})
                })
        
        # Retrieve from SHC cases
        if self.shc_corpus and self.shc_embeddings is not None:
            if torch.cuda.is_available():
                shc_emb = self.shc_embeddings.to('cuda')
            else:
                shc_emb = self.shc_embeddings
            
            shc_scores = util.cos_sim(query_embedding, shc_emb)[0]
            top_shc = torch.topk(shc_scores, k=min(top_k, len(shc_scores)))
            for idx in top_shc.indices:
                doc = self.shc_corpus[idx]
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": float(shc_scores[idx] * weights['shc']),
                    "source": doc.get('source', 'shc'),
                    "type": "case_law",
                    "title": doc.get('title', 'SHC Case'),
                    "metadata": doc.get('metadata', {})
                })
        
        # Retrieve from CrPC
        if self.crpc_corpus and self.crpc_embeddings is not None:
            if torch.cuda.is_available():
                crpc_emb = self.crpc_embeddings.to('cuda')
            else:
                crpc_emb = self.crpc_embeddings
            
            crpc_scores = util.cos_sim(query_embedding, crpc_emb)[0]
            top_crpc = torch.topk(crpc_scores, k=min(top_k, len(crpc_scores)))
            for idx in top_crpc.indices:
                doc = self.crpc_corpus[idx]
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": float(crpc_scores[idx] * weights['crpc']),
                    "source": doc.get('source', 'crpc'),
                    "type": "crpc",
                    "title": doc.get('title', 'CrPC Section'),
                    "metadata": doc.get('metadata', {})
                })
        
        # Retrieve from Constitution
        if self.constitution_corpus and self.constitution_embeddings is not None:
            if torch.cuda.is_available():
                const_emb = self.constitution_embeddings.to('cuda')
            else:
                const_emb = self.constitution_embeddings
            
            const_scores = util.cos_sim(query_embedding, const_emb)[0]
            top_const = torch.topk(const_scores, k=min(top_k, len(const_scores)))
            for idx in top_const.indices:
                doc = self.constitution_corpus[idx]
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": float(const_scores[idx] * weights['constitution']),
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
            top_struct = torch.topk(struct_scores, k=min(top_k * 2, len(struct_scores)))  # Get more from structured
            for idx in top_struct.indices:
                doc = self.structured_corpus[idx]
                all_results.append({
                    "text": doc.get('text', ''),
                    "score": float(struct_scores[idx] * weights.get('structured', 1.0)),
                    "source": doc.get('source', 'structured_data'),
                    "type": doc.get('category', 'principle'),
                    "title": doc.get('title', doc.get('category', 'Legal Principle')),
                    "metadata": doc.get('metadata', {})
                })
        
        # Sort by weighted score and return top_k
        all_results.sort(key=lambda x: x['score'], reverse=True)
        return all_results[:top_k]
    
    def format_context_with_references(self, retrieved_docs: List[Dict], max_length: int = 2000) -> Tuple[str, List[Dict]]:
        """Format context with proper references"""
        context_parts = []
        references = []
        
        current_length = 0
        for i, doc in enumerate(retrieved_docs):
            text = doc['text']
            source = doc['source']
            title = doc['title']
            doc_type = doc.get('type', 'unknown')
            
            if current_length + len(text) > max_length:
                break
            
            # Format based on type
            if doc_type == 'ppc':
                context_parts.append(f"[PPC Section {doc.get('metadata', {}).get('section_number', '')}]: {text}")
                references.append({
                    "type": "PPC",
                    "section": doc.get('metadata', {}).get('section_number', ''),
                    "title": title
                })
            elif doc_type == 'case_law':
                case_no = doc.get('metadata', {}).get('case_no', '')
                context_parts.append(f"[SHC Case {case_no}]: {text}")
                references.append({
                    "type": "Case Law",
                    "case_no": case_no,
                    "title": title,
                    "pdf_url": doc.get('metadata', {}).get('pdf_url', '')
                })
            elif doc_type == 'crpc':
                context_parts.append(f"[CrPC Section]: {text}")
                references.append({
                    "type": "CrPC",
                    "title": title
                })
            elif doc_type == 'constitution':
                context_parts.append(f"[Constitution]: {text}")
                references.append({
                    "type": "Constitution",
                    "title": title
                })
            else:
                context_parts.append(f"[{title}]: {text}")
                references.append({
                    "type": doc_type,
                    "title": title
                })
            
            current_length += len(text)
        
        context = "\n\n".join(context_parts)
        return context, references

