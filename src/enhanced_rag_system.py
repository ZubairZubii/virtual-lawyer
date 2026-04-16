import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch
from tqdm import tqdm
import pickle
import os
from typing import List, Dict
import re

class EnhancedRAGSystem:
    """Enhanced RAG with better retrieval and Pakistan Criminal Law focus"""
    
    def __init__(self, corpus_path="./data/processed/comprehensive_rag_corpus.json", 
                 embeddings_dir="./data/embeddings"):
        self.corpus_path = corpus_path
        self.embeddings_dir = embeddings_dir
        os.makedirs(embeddings_dir, exist_ok=True)
        
        print("🧠 Loading enhanced embedding model...")
        # Use better model for legal domain
        self.embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        if torch.cuda.is_available():
            self.embed_model = self.embed_model.to('cuda')
        
        self.corpus = None
        self.corpus_embeddings = None
        self.metadata_index = {}  # For quick lookups
        
    def load_corpus(self):
        """Load RAG corpus with metadata indexing"""
        print(f"📚 Loading corpus from {self.corpus_path}...")
        
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            self.corpus = json.load(f)
        
        # Create metadata index for faster searching
        self._build_metadata_index()
        
        print(f"✅ Loaded {len(self.corpus)} documents")
        print(f"   PPC sections: {self.metadata_index['ppc_count']}")
        print(f"   Case laws: {self.metadata_index['case_count']}")
        return self.corpus
    
    def _build_metadata_index(self):
        """Build index for quick metadata lookups"""
        ppc_count = 0
        case_count = 0
        section_map = {}
        
        for idx, doc in enumerate(self.corpus):
            source = doc.get('source', '')
            
            if 'ppc' in source.lower():
                ppc_count += 1
                # Extract section numbers
                sections = re.findall(r'Section\s+(\d+[A-Z]?)', doc['text'], re.IGNORECASE)
                for sec in sections:
                    if sec not in section_map:
                        section_map[sec] = []
                    section_map[sec].append(idx)
            
            if 'case' in source.lower():
                case_count += 1
        
        self.metadata_index = {
            'ppc_count': ppc_count,
            'case_count': case_count,
            'section_map': section_map
        }
    
    def create_embeddings(self, force_rebuild=False):
        """Create embeddings with progress tracking"""
        embeddings_path = os.path.join(self.embeddings_dir, "enhanced_corpus_embeddings.pkl")
        
        if os.path.exists(embeddings_path) and not force_rebuild:
            print(f"📦 Loading existing embeddings...")
            with open(embeddings_path, 'rb') as f:
                self.corpus_embeddings = pickle.load(f)
            print(f"✅ Loaded embeddings for {len(self.corpus_embeddings)} documents")
            return self.corpus_embeddings
        
        if self.corpus is None:
            self.load_corpus()
        
        print(f"🔄 Creating embeddings for {len(self.corpus)} documents...")
        
        texts = [doc['text'] for doc in self.corpus]
        
        batch_size = 32
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Creating embeddings"):
            batch = texts[i:i+batch_size]
            embeddings = self.embed_model.encode(batch, convert_to_tensor=True, show_progress_bar=False)
            all_embeddings.append(embeddings.cpu())
        
        self.corpus_embeddings = torch.cat(all_embeddings, dim=0)
        
        with open(embeddings_path, 'wb') as f:
            pickle.dump(self.corpus_embeddings, f)
        
        print(f"✅ Created and saved embeddings")
        return self.corpus_embeddings
    
    def retrieve_by_section(self, section_number: str) -> List[Dict]:
        """Retrieve documents by PPC section number"""
        section_map = self.metadata_index.get('section_map', {})
        
        if section_number in section_map:
            indices = section_map[section_number]
            return [self.corpus[idx] for idx in indices]
        return []
    
    def retrieve(self, query: str, top_k: int = 5, boost_ppc: bool = True) -> List[Dict]:
        """Enhanced retrieval with section detection and PPC boosting"""
        
        if self.corpus_embeddings is None:
            self.create_embeddings()
        
        # Check if query mentions specific section
        section_match = re.search(r'Section\s+(\d+[A-Z]?)', query, re.IGNORECASE)
        if section_match:
            section_num = section_match.group(1)
            section_docs = self.retrieve_by_section(section_num)
            if section_docs:
                print(f"🎯 Found {len(section_docs)} docs for Section {section_num}")
                return section_docs[:top_k]
        
        # Semantic search
        query_embedding = self.embed_model.encode(query, convert_to_tensor=True)
        
        if torch.cuda.is_available():
            query_embedding = query_embedding.to('cuda')
            corpus_emb = self.corpus_embeddings.to('cuda')
        else:
            corpus_emb = self.corpus_embeddings
        
        cos_scores = util.cos_sim(query_embedding, corpus_emb)[0]
        
        # Boost PPC documents if enabled
        if boost_ppc:
            for idx, doc in enumerate(self.corpus):
                if 'ppc' in doc.get('source', '').lower():
                    cos_scores[idx] *= 1.2  # 20% boost for PPC docs
        
        top_results = torch.topk(cos_scores, k=min(top_k, len(cos_scores)))
        
        retrieved_docs = []
        for score, idx in zip(top_results.values, top_results.indices):
            doc = self.corpus[idx]
            retrieved_docs.append({
                "text": doc['text'],
                "score": float(score),
                "source": doc.get('source', 'unknown'),
                "title": doc.get('title', 'N/A')
            })
        
        return retrieved_docs
    
    def format_context(self, retrieved_docs: List[Dict], max_length: int = 2000) -> str:
        """Format with better structure"""
        if not retrieved_docs:
            return ""
        
        context = "📚 Relevant Pakistan Criminal Law Information:\n\n"
        
        current_length = 0
        for i, doc in enumerate(retrieved_docs, 1):
            doc_text = doc['text']
            source = doc.get('source', 'unknown')
            
            if current_length + len(doc_text) > max_length:
                break
            
            context += f"[Source {i}: {source}]\n{doc_text}\n\n"
            current_length += len(doc_text)
        
        return context.strip()
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        if self.corpus is None:
            self.load_corpus()
        
        return {
            "total_documents": len(self.corpus),
            "ppc_sections": self.metadata_index['ppc_count'],
            "case_laws": self.metadata_index['case_count'],
            "indexed_sections": len(self.metadata_index['section_map'])
        }

if __name__ == "__main__":
    rag = EnhancedRAGSystem()
    rag.load_corpus()
    rag.create_embeddings()
    
    print("\n" + "="*60)
    print("RAG STATS:")
    print(json.dumps(rag.get_stats(), indent=2))
    
    # Test queries
    test_queries = [
        "What is Section 302 PPC?",
        "Punishment for murder in Pakistan",
        "Rights during arrest"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        results = rag.retrieve(query, top_k=3)
        for i, doc in enumerate(results, 1):
            print(f"\n[{i}] Score: {doc['score']:.3f} | Source: {doc['source']}")
            print(doc['text'][:200] + "...")