import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch
from tqdm import tqdm
import pickle
import os

class RAGSystem:
    def __init__(self, corpus_path="./data/processed/full_rag_corpus.json", 
                 embeddings_dir="./data/embeddings"):
        self.corpus_path = corpus_path
        self.embeddings_dir = embeddings_dir
        os.makedirs(embeddings_dir, exist_ok=True)
        
        # Load embedding model (lightweight for 6GB GPU)
        print("🧠 Loading embedding model...")
        self.embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Move to GPU if available
        if torch.cuda.is_available():
            self.embed_model = self.embed_model.to('cuda')
        
        self.corpus = None
        self.corpus_embeddings = None
    
    def load_corpus(self):
        """Load RAG corpus"""
        print(f"📚 Loading corpus from {self.corpus_path}...")
        
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            self.corpus = json.load(f)
        
        print(f"✅ Loaded {len(self.corpus)} documents")
        return self.corpus
    
    def create_embeddings(self, force_rebuild=False):
        """Create embeddings for entire corpus"""
        embeddings_path = os.path.join(self.embeddings_dir, "corpus_embeddings.pkl")
        
        # Check if embeddings already exist
        if os.path.exists(embeddings_path) and not force_rebuild:
            print(f"📦 Loading existing embeddings...")
            with open(embeddings_path, 'rb') as f:
                self.corpus_embeddings = pickle.load(f)
            print(f"✅ Loaded embeddings for {len(self.corpus_embeddings)} documents")
            return self.corpus_embeddings
        
        # Create new embeddings
        if self.corpus is None:
            self.load_corpus()
        
        print(f"🔄 Creating embeddings for {len(self.corpus)} documents...")
        print("   ⏳ This may take 5-10 minutes...")
        
        # Extract texts
        texts = [doc['text'] for doc in self.corpus]
        
        # Create embeddings in batches
        batch_size = 32
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size)):
            batch = texts[i:i+batch_size]
            embeddings = self.embed_model.encode(batch, convert_to_tensor=True, show_progress_bar=False)
            all_embeddings.append(embeddings.cpu())
        
        # Concatenate all embeddings
        self.corpus_embeddings = torch.cat(all_embeddings, dim=0)
        
        # Save embeddings
        with open(embeddings_path, 'wb') as f:
            pickle.dump(self.corpus_embeddings, f)
        
        print(f"✅ Created and saved embeddings")
        print(f"   Shape: {self.corpus_embeddings.shape}")
        print(f"   Saved to: {embeddings_path}")
        
        return self.corpus_embeddings
    
    def retrieve(self, query, top_k=5):
        """Retrieve most relevant documents for a query"""
        
        if self.corpus_embeddings is None:
            print("⚠️  Embeddings not loaded! Loading now...")
            self.create_embeddings()
        
        # Encode query
        query_embedding = self.embed_model.encode(query, convert_to_tensor=True)
        
        # Move to same device
        if torch.cuda.is_available():
            query_embedding = query_embedding.to('cuda')
            corpus_emb = self.corpus_embeddings.to('cuda')
        else:
            corpus_emb = self.corpus_embeddings
        
        # Compute similarity
        cos_scores = util.cos_sim(query_embedding, corpus_emb)[0]
        
        # Get top-k results
        top_results = torch.topk(cos_scores, k=min(top_k, len(cos_scores)))
        
        retrieved_docs = []
        for score, idx in zip(top_results.values, top_results.indices):
            doc = self.corpus[idx]
            retrieved_docs.append({
                "text": doc['text'],
                "score": float(score),
                "source": doc.get('source', 'unknown')
            })
        
        return retrieved_docs
    
    def format_context(self, retrieved_docs, max_length=2000):
        """Format retrieved documents as context for LLM"""
        context = "Relevant Legal Information:\n\n"
        
        current_length = 0
        for i, doc in enumerate(retrieved_docs, 1):
            doc_text = doc['text']
            if current_length + len(doc_text) > max_length:
                break
            context += f"[{i}] {doc_text}\n\n"
            current_length += len(doc_text)
        
        return context.strip()

# Test the RAG system
if __name__ == "__main__":
    print("="*60)
    print("TESTING RAG SYSTEM")
    print("="*60)
    
    rag = RAGSystem()
    
    # Load corpus and create embeddings
    rag.load_corpus()
    rag.create_embeddings()
    
    # Test queries
    test_queries = [
        "What is the punishment for murder under Section 302?",
        "How to file an FIR?",
        "What are my rights when arrested?",
        "Can I get bail in theft case?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        results = rag.retrieve(query, top_k=3)
        
        for i, doc in enumerate(results, 1):
            print(f"\n[Result {i}] (Score: {doc['score']:.3f}) (Source: {doc['source']})")
            print(f"{doc['text'][:300]}...")
        
        print("\n" + "="*60)
        input("Press Enter for next query...")