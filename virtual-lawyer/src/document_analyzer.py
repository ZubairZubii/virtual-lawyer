"""
Document Analysis Module
Handles document upload, text extraction, chunking, and Q&A
"""
import os
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

# PDF processing
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    try:
        import fitz  # PyMuPDF
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

# DOCX processing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Embeddings and vector search
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

class DocumentAnalyzer:
    """
    Document Analysis System:
    1. Upload document (PDF/DOCX)
    2. Extract and clean text
    3. Chunk text
    4. Create embeddings
    5. Answer questions using RAG
    """
    
    def __init__(self, 
                 upload_dir: str = "./data/uploads",
                 embeddings_dir: str = "./data/embeddings/documents",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize Document Analyzer
        
        Args:
            upload_dir: Directory to store uploaded documents
            embeddings_dir: Directory to store document embeddings
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.upload_dir = Path(upload_dir)
        self.embeddings_dir = Path(embeddings_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create directories
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            print("Loading embedding model for document analysis...")
            self.embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        else:
            self.embed_model = None
            print("Warning: Embeddings not available. Install sentence-transformers")
        
        # Store active documents in memory (doc_id -> chunks, embeddings)
        self.active_documents: Dict[str, Dict] = {}
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ValueError("PDF processing not available. Install pdfplumber or PyMuPDF")
        
        text = ""
        
        # Try pdfplumber first
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            # Fallback to PyMuPDF
            try:
                import fitz
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            except Exception as e:
                raise ValueError(f"Error extracting PDF text: {e}")
        
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            raise ValueError("DOCX processing not available. Install python-docx")
        
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Error extracting DOCX text: {e}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text:
        - Remove excessive whitespace
        - Normalize legal phrases
        - Remove watermarks/headers/footers
        - Fix encoding issues
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common watermarks/headers
        watermark_patterns = [
            r'CONFIDENTIAL',
            r'DRAFT',
            r'Page \d+',
            r'©.*?',
        ]
        for pattern in watermark_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Normalize legal phrases
        legal_replacements = {
            'FIR No': 'FIR Number',
            'FIR No.': 'FIR Number',
            'S. ': 'Section ',
            'S.': 'Section',
            'PPC': 'Pakistan Penal Code',
            'CrPC': 'Code of Criminal Procedure',
        }
        
        for old, new in legal_replacements.items():
            text = text.replace(old, new)
        
        # Remove judge signatures (common patterns)
        text = re.sub(r'Judge.*?Court', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Dated:.*?\n', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[Dict]:
        """
        Break text into chunks with overlap
        
        Returns:
            List of chunk dicts with 'text', 'start', 'end', 'chunk_id'
        """
        chunks = []
        words = text.split()
        
        if not words:
            return chunks
        
        start = 0
        chunk_id = 0
        
        while start < len(words):
            # Calculate end position
            end = min(start + self.chunk_size, len(words))
            
            # Extract chunk
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text,
                    'start': start,
                    'end': end,
                    'chunk_id': chunk_id,
                    'char_start': len(' '.join(words[:start])),
                    'char_end': len(' '.join(words[:end]))
                })
                chunk_id += 1
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap
            if start >= len(words):
                break
        
        return chunks
    
    def create_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """Create embeddings for text chunks"""
        if not self.embed_model:
            raise ValueError("Embedding model not available")
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embed_model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def upload_document(self, file_path: str, file_name: str = None) -> Dict:
        """
        Upload and process document
        
        Args:
            file_path: Path to uploaded file
            file_name: Original file name
        
        Returns:
            Dict with doc_id, status, chunks_count, etc.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate document ID
        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        doc_id = f"doc_{file_hash[:12]}_{int(datetime.now().timestamp())}"
        
        # Determine file type
        ext = file_path.suffix.lower()
        
        # Extract text
        if ext == '.pdf':
            text = self.extract_text_from_pdf(str(file_path))
        elif ext in ['.docx', '.doc']:
            text = self.extract_text_from_docx(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text.strip():
            raise ValueError("No text extracted from document")
        
        # Chunk text
        chunks = self.chunk_text(cleaned_text)
        
        if not chunks:
            raise ValueError("No chunks created from document")
        
        # Create embeddings
        embeddings = None
        if self.embed_model:
            embeddings = self.create_embeddings(chunks)
        
        # Save document info
        doc_info = {
            'doc_id': doc_id,
            'file_name': file_name or file_path.name,
            'file_path': str(file_path),
            'file_type': ext,
            'text_length': len(cleaned_text),
            'chunks_count': len(chunks),
            'uploaded_at': datetime.now().isoformat(),
            'chunks': chunks,
            'embeddings': embeddings.tolist() if embeddings is not None else None
        }
        
        # Store in memory
        self.active_documents[doc_id] = doc_info
        
        # Save to disk
        doc_file = self.embeddings_dir / f"{doc_id}.json"
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(doc_info, f, indent=2, ensure_ascii=False)
        
        return {
            'doc_id': doc_id,
            'file_name': doc_info['file_name'],
            'chunks_count': len(chunks),
            'text_length': len(cleaned_text),
            'status': 'success'
        }
    
    def search_chunks(self, doc_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant chunks in document using semantic search
        
        Args:
            doc_id: Document ID
            query: Search query
            top_k: Number of top results
        
        Returns:
            List of relevant chunks with scores
        """
        if doc_id not in self.active_documents:
            # Try to load from disk
            doc_file = self.embeddings_dir / f"{doc_id}.json"
            if doc_file.exists():
                with open(doc_file, 'r', encoding='utf-8') as f:
                    self.active_documents[doc_id] = json.load(f)
            else:
                raise ValueError(f"Document {doc_id} not found")
        
        doc_info = self.active_documents[doc_id]
        chunks = doc_info['chunks']
        
        if not self.embed_model:
            # Fallback to keyword search
            query_lower = query.lower()
            results = []
            for chunk in chunks:
                score = chunk['text'].lower().count(query_lower) / len(chunk['text'].split())
                if score > 0:
                    results.append({**chunk, 'score': score})
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
        
        # Semantic search
        query_embedding = self.embed_model.encode([query], convert_to_numpy=True)
        
        if doc_info['embeddings']:
            chunk_embeddings = np.array(doc_info['embeddings'])
        else:
            # Create embeddings on the fly
            chunk_embeddings = self.create_embeddings(chunks)
            doc_info['embeddings'] = chunk_embeddings.tolist()
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            chunk = chunks[idx]
            results.append({
                **chunk,
                'score': float(similarities[idx])
            })
        
        return results
    
    def answer_question(self, doc_id: str, question: str, context_from_rag: str = None) -> Dict:
        """
        Answer question about document
        
        Args:
            doc_id: Document ID
            question: User question
            context_from_rag: Additional context from main RAG system
        
        Returns:
            Dict with answer, relevant_chunks, confidence
        """
        # Search for relevant chunks
        relevant_chunks = self.search_chunks(doc_id, question, top_k=5)
        
        # Build context from chunks
        context = "\n\n".join([
            f"[Chunk {i+1}]: {chunk['text']}"
            for i, chunk in enumerate(relevant_chunks)
        ])
        
        # Add main RAG context if provided
        if context_from_rag:
            context = f"{context_from_rag}\n\n--- Document Context ---\n{context}"
        
        return {
            'answer': None,  # Will be generated by LLM
            'relevant_chunks': relevant_chunks,
            'context': context,
            'chunks_used': len(relevant_chunks),
            'confidence': max([c['score'] for c in relevant_chunks]) if relevant_chunks else 0.0
        }
    
    def extract_facts(self, doc_id: str) -> Dict:
        """
        Automatically extract structured facts from document
        
        Returns:
            Dict with extracted facts (FIR number, sections, dates, etc.)
        """
        if doc_id not in self.active_documents:
            doc_file = self.embeddings_dir / f"{doc_id}.json"
            if doc_file.exists():
                with open(doc_file, 'r', encoding='utf-8') as f:
                    self.active_documents[doc_id] = json.load(f)
            else:
                raise ValueError(f"Document {doc_id} not found")
        
        doc_info = self.active_documents[doc_id]
        full_text = ' '.join([chunk['text'] for chunk in doc_info['chunks']])
        
        # Extract structured information using regex patterns
        facts = {
            'fir_number': None,
            'fir_date': None,
            'police_station': None,
            'sections': [],
            'accused': [],
            'complainant': None,
            'district': None,
            'case_status': None,
            'court': None,
            'judge': None,
        }
        
        # Extract FIR number
        fir_patterns = [
            r'FIR\s+No[.:]?\s*(\d+/\d{4})',
            r'FIR\s+Number[.:]?\s*(\d+/\d{4})',
            r'FIR\s+(\d+/\d{4})',
        ]
        for pattern in fir_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                facts['fir_number'] = match.group(1)
                break
        
        # Extract sections
        section_patterns = [
            r'Section\s+(\d+[A-Z]?)\s+PPC',
            r'Section\s+(\d+[A-Z]?)\s+CrPC',
            r'S[.]?\s*(\d+[A-Z]?)\s+PPC',
            r'(\d+[A-Z]?)\s+PPC',
        ]
        for pattern in section_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            facts['sections'].extend(matches)
        facts['sections'] = list(set(facts['sections']))  # Remove duplicates
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+\w+\s+\d{4})',
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, full_text)
            dates.extend(matches)
        if dates:
            facts['fir_date'] = dates[0]  # Usually first date is FIR date
        
        # Extract police station
        ps_patterns = [
            r'Police\s+Station[.:]?\s*([A-Z][A-Za-z\s]+)',
            r'PS[.:]?\s*([A-Z][A-Za-z\s]+)',
        ]
        for pattern in ps_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                facts['police_station'] = match.group(1).strip()
                break
        
        return facts
    
    def get_document_summary(self, doc_id: str) -> str:
        """Get summary of document"""
        if doc_id not in self.active_documents:
            doc_file = self.embeddings_dir / f"{doc_id}.json"
            if doc_file.exists():
                with open(doc_file, 'r', encoding='utf-8') as f:
                    self.active_documents[doc_id] = json.load(f)
            else:
                raise ValueError(f"Document {doc_id} not found")
        
        doc_info = self.active_documents[doc_id]
        full_text = ' '.join([chunk['text'] for chunk in doc_info['chunks']])
        
        # Return first 500 characters as summary (can be enhanced with LLM)
        return full_text[:500] + "..." if len(full_text) > 500 else full_text





















