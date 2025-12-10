"""
Three-Stage Pipeline: Local Model + RAG + Groq Direct + Groq Formatter
Long-term solution for better answer quality
"""
import time
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from multi_layer_pipeline import MultiLayerPipeline
    from multi_source_rag import MultiSourceRAG
except ImportError:
    print("Warning: Could not import multi_layer_pipeline or multi_source_rag")

class ThreeStagePipeline:
    """
    Enhanced three-stage pipeline:
    Stage 1: Local model + RAG (initial answer)
    Stage 2: Groq direct answer (alternative perspective)
    Stage 3: Groq formatter (combines both, creates best answer)
    """
    
    def __init__(self,
                 peft_model_path: str = "./models/fine-tuned/golden_model/final_golden_model",
                 formatter_type: str = "groq",
                 formatter_api_key: Optional[str] = None):
        """
        Initialize three-stage pipeline
        
        Args:
            peft_model_path: Path to fine-tuned model
            formatter_type: "groq" for Groq API
            formatter_api_key: Groq API key (or from config)
        """
        print("🚀 Initializing Three-Stage Pipeline...")
        
        # Stage 1: Local model + RAG
        print("   Stage 1: Local model + RAG...")
        try:
            self.stage1_pipeline = MultiLayerPipeline(
                peft_model_path=peft_model_path
            )
            self.rag = MultiSourceRAG()
            print("   ✅ Stage 1 ready")
        except Exception as e:
            print(f"   ⚠️  Stage 1 error: {e}")
            self.stage1_pipeline = None
            self.rag = None
        
        # Stage 2 & 3: Groq
        print("   Stage 2 & 3: Groq API...")
        self.groq_available = False
        self.groq_api_key = formatter_api_key
        
        if not self.groq_api_key:
            # Try to load from config
            try:
                from config import GROQ_API_KEY
                self.groq_api_key = GROQ_API_KEY
            except:
                pass
        
        if self.groq_api_key:
            try:
                # Try groq package first
                try:
                    from groq import Groq
                    self.groq_client = Groq(api_key=self.groq_api_key)
                except ImportError:
                    # Fallback to requests-based Groq API
                    import requests
                    self.groq_client = None
                    self.groq_api_key = self.groq_api_key
                    self._use_requests = True
                self.groq_available = True
                print("   ✅ Groq API ready")
            except Exception as e:
                print(f"   ⚠️  Groq error: {e}")
                self.groq_available = False
                self._use_requests = False
        else:
            print("   ⚠️  Groq API key not found")
        
        print("✅ Three-Stage Pipeline initialized!\n")
    
    def _get_groq_direct_answer(self, question: str, context: str, references: List[Dict]) -> Dict:
        """
        Stage 2: Get direct answer from Groq
        
        Returns:
            Dict with 'answer', 'response_time'
        """
        if not self.groq_available:
            return {'answer': '', 'response_time': 0, 'error': 'Groq not available'}
        
        start_time = time.time()
        
        try:
            # Build prompt for Groq
            ref_text = ""
            if references:
                ref_text = "\n".join([
                    f"- {ref.get('type', 'Unknown')}: {ref.get('case_no', ref.get('title', 'N/A'))}"
                    for ref in references[:5]
                ])
            
            prompt = f"""You are an expert Pakistan criminal law assistant. Answer accurately and completely.

LEGAL CONTEXT:
{context[:2000]}

REFERENCES:
{ref_text}

QUESTION: {question}

CRITICAL ANSWER REQUIREMENTS:
1. **Address ALL parts of the question** - If question has multiple aspects, answer ALL of them
2. **Answer the specific scenario** - Don't just give general law, address the exact situation
3. **Include practical consequences** - Explain what happens, not just what the law says

LEGAL ACCURACY RULES:
1. Ocular evidence has PRIMACY over medical evidence
2. Medical evidence is CORROBORATIVE only
3. Only cite cases from references above
4. Use standard citation formats: SCMR, PLD, YLR
5. DO NOT invent case numbers

COMPROMISE/FAMILY WISHES (if relevant):
- Explain whether compromise is possible (Section 345 CrPC)
- Mention diyat (blood money) if applicable
- Explain court's discretion vs family wishes
- State that case can proceed even if family doesn't want punishment

Provide a clear, complete, and legally accurate answer that addresses ALL aspects of the question:"""
            
            # Call Groq
            if hasattr(self, '_use_requests') and self._use_requests:
                # Use requests-based API
                import requests
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "You are an expert Pakistan criminal law assistant. Provide accurate, legally correct answers."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    answer = result['choices'][0]['message']['content'].strip()
                else:
                    raise Exception(f"Groq API error: {response.status_code}")
            else:
                # Use groq package
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert Pakistan criminal law assistant. Provide accurate, legally correct answers."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                answer = response.choices[0].message.content.strip()
            response_time = time.time() - start_time
            
            return {
                'answer': answer,
                'response_time': response_time,
                'error': None
            }
        except Exception as e:
            return {
                'answer': '',
                'response_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _format_with_groq(self, question: str, stage1_answer: str, stage2_answer: str, 
                         context: str, references: List[Dict]) -> Dict:
        """
        Stage 3: Use Groq to combine both answers and create best formatted answer
        
        Returns:
            Dict with 'answer', 'response_time'
        """
        if not self.groq_available:
            # Fallback to stage1 answer
            return {
                'answer': stage1_answer,
                'response_time': 0,
                'formatted': False
            }
        
        start_time = time.time()
        
        try:
            ref_text = ""
            if references:
                ref_text = "\n".join([
                    f"- {ref.get('type', 'Unknown')}: {ref.get('case_no', ref.get('title', 'N/A'))}"
                    for ref in references[:5]
                ])
            
            prompt = f"""You are formatting a legal answer about Pakistan criminal law.

ORIGINAL QUESTION: {question}

STAGE 1 ANSWER (Local Model + RAG):
{stage1_answer}

STAGE 2 ANSWER (Groq Direct):
{stage2_answer}

RELEVANT LEGAL CONTEXT:
{context[:1500]}

REFERENCES:
{ref_text}

TASK: Combine both answers to create the BEST, most accurate, and well-formatted answer.

CRITICAL REQUIREMENTS:
1. **Evidence Priority Questions**: MUST state BOTH:
   - "Ocular evidence has primacy" 
   - "Medical evidence is corroborative"
   
2. **Witness Credibility Questions**: MUST include:
   - Material vs minor contradictions
   - Corroboration requirement
   - Benefit of doubt principle

3. **Case Citations**: 
   - ONLY use citations from references list
   - DO NOT use SHC case numbers (Cr.J.A, Cr.Rev) as citations
   - Use standard formats: SCMR, PLD, YLR
   - If no case in references, say "as established in Supreme Court precedents"

4. **Answer Quality**:
   - Use the BEST parts from both answers
   - Remove any incorrect information
   - Ensure legal accuracy
   - Make it clear and well-structured

5. **Format**:
   - Start directly with the answer (no prefixes)
   - Use proper legal terminology
   - Include relevant case citations if available
   - Keep it concise but complete

COMBINED AND FORMATTED ANSWER:"""
            
            if hasattr(self, '_use_requests') and self._use_requests:
                # Use requests-based API
                import requests
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "You are an expert legal formatter. Combine answers to create the best, most accurate legal response."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1500
                    },
                    timeout=45
                )
                if response.status_code == 200:
                    result = response.json()
                    formatted_answer = result['choices'][0]['message']['content'].strip()
                else:
                    raise Exception(f"Groq API error: {response.status_code}")
            else:
                # Use groq package
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert legal formatter. Combine answers to create the best, most accurate legal response."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1500
                )
                formatted_answer = response.choices[0].message.content.strip()
            response_time = time.time() - start_time
            
            return {
                'answer': formatted_answer,
                'response_time': response_time,
                'formatted': True
            }
        except Exception as e:
            print(f"   ⚠️  Groq formatting error: {e}")
            # Fallback to stage1 answer
            return {
                'answer': stage1_answer,
                'response_time': time.time() - start_time,
                'formatted': False
            }
    
    def generate_answer(self, question: str, use_formatter: bool = True) -> Dict:
        """
        Generate answer using three-stage pipeline
        
        Args:
            question: User question
            use_formatter: Whether to use Stage 3 formatter
        
        Returns:
            Dict with answer, references, timing, etc.
        """
        total_start = time.time()
        
        # Stage 1: Local model + RAG
        stage1_start = time.time()
        stage1_result = None
        context = ""
        references = []
        
        if self.stage1_pipeline and self.rag:
            try:
                # Retrieve context
                retrieved_docs = self.rag.retrieve(question, top_k=5)
                context = "\n\n".join([
                    f"[{i+1}] {doc.get('text', '')}"
                    for i, doc in enumerate(retrieved_docs)
                ])
                
                # Format references
                references = [
                    {
                        'type': doc.get('type', 'unknown'),
                        'title': doc.get('title', ''),
                        'case_no': doc.get('case_no', ''),
                        'source': doc.get('source', '')
                    }
                    for doc in retrieved_docs
                ]
                
                # Generate answer (MultiLayerPipeline uses RAG internally)
                stage1_result = self.stage1_pipeline.generate_answer(question)
                
                # Use our retrieved references if pipeline didn't provide them
                if stage1_result and not stage1_result.get('references'):
                    stage1_result['references'] = references
            except Exception as e:
                print(f"   ⚠️  Stage 1 error: {e}")
                stage1_result = {'answer': '', 'error': str(e)}
        
        stage1_time = time.time() - stage1_start
        stage1_answer = stage1_result.get('answer', '') if stage1_result else ''
        
        # Stage 2: Groq direct answer (if available and use_formatter)
        stage2_answer = ''
        stage2_time = 0
        
        if use_formatter and self.groq_available:
            stage2_start = time.time()
            stage2_result = self._get_groq_direct_answer(question, context, references)
            stage2_answer = stage2_result.get('answer', '')
            stage2_time = stage2_result.get('response_time', 0)
        
        # Stage 3: Groq formatter (combine both)
        final_answer = stage1_answer
        stage3_time = 0
        formatted = False
        
        if use_formatter and self.groq_available and stage2_answer:
            stage3_result = self._format_with_groq(
                question=question,
                stage1_answer=stage1_answer,
                stage2_answer=stage2_answer,
                context=context,
                references=references
            )
            final_answer = stage3_result.get('answer', stage1_answer)
            stage3_time = stage3_result.get('response_time', 0)
            formatted = stage3_result.get('formatted', False)
        
        total_time = time.time() - total_start
        
        return {
            'answer': final_answer,
            'references': references,
            'sources_count': len(references),
            'response_time': total_time,
            'stage1_time': stage1_time,
            'stage2_time': stage2_time,
            'stage3_time': stage3_time,
            'formatted': formatted,
            'stage1_answer': stage1_answer,
            'stage2_answer': stage2_answer if stage2_answer else None
        }

