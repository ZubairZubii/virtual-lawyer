"""
Two-Stage Pipeline for Pakistan Criminal Law Chatbot
Stage 1: Your fine-tuned model (retrieval + initial answer)
Stage 2: Formatting model (improves and formats the answer)

This is the PRODUCTION-READY version optimized for best performance.
"""
import os
import time
import json
import re
from typing import Dict, Optional, List
import requests
from multi_layer_pipeline import MultiLayerPipeline

# Import config
import sys
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from config import PIPELINE_CONFIG, GROQ_API_KEY
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
except ImportError:
    # Fallback if config not found
    PIPELINE_CONFIG = {
        "formatter_type": "groq",
        # Groq decommissioned `llama-3.1-70b-versatile`. Use a supported model.
        "formatter_model": "llama-3.3-70b-versatile",
        "stage1": {"max_new_tokens": 150, "temperature": 0.2, "top_k": 3, "context_max_length": 1500},
        "stage2": {"temperature": 0.3, "max_tokens": 600, "top_p": 0.9}
    }

class TwoStagePipeline:
    """
    Two-stage pipeline:
    1. Your model: Retrieves context and generates initial answer
    2. Formatting model: Formats and improves the answer
    """
    
    def __init__(self,
                 peft_model_path="./models/final_model_v5",
                 formatter_type="groq",  # "groq", "huggingface", "openai", "claude"
                 formatter_api_key=None):
        """
        Initialize two-stage pipeline
        
        Args:
            peft_model_path: Path to your fine-tuned model
            formatter_type: Type of formatting model to use
            formatter_api_key: API key for formatting model (if needed)
        """
        print("=" * 60)
        print("INITIALIZING TWO-STAGE PIPELINE")
        print("=" * 60)
        
        # Stage 1: Your fine-tuned model
        print("\nStage 1: Loading your fine-tuned model...")
        self.stage1_model = MultiLayerPipeline(
            peft_model_path=peft_model_path,
            use_rag=True
        )
        print("Stage 1 ready!")
        
        # Stage 2: Formatting model
        print(f"\nStage 2: Setting up {formatter_type} formatter...")
        self.formatter_type = formatter_type
        self.formatter_api_key = formatter_api_key or os.getenv(f"{formatter_type.upper()}_API_KEY")
        
        if not self.formatter_api_key and formatter_type in ["groq", "openai", "claude"]:
            print(f"WARNING: {formatter_type.upper()}_API_KEY not found!")
            print(f"Set it as environment variable or pass as argument")
            print("Continuing without formatter (will use Stage 1 only)...")
            self.use_formatter = False
        else:
            self.use_formatter = True
            print(f"Stage 2 ready! Using {formatter_type}")
        
        print("\n" + "=" * 60)
        print("TWO-STAGE PIPELINE READY")
        print("=" * 60)
    
    def _format_with_groq(self, initial_answer: str, question: str, context: str, references: list) -> str:
        """Format answer using Groq API (FREE, FAST) - OPTIMIZED FOR PAKISTAN CRIMINAL LAW"""
        
        # Build references text
        ref_text = ""
        if references:
            ref_text = "\nREFERENCES:\n"
            for i, ref in enumerate(references[:3], 1):
                if ref.get('type') == 'PPC':
                    ref_text += f"{i}. PPC Section {ref.get('section', 'N/A')}\n"
                elif ref.get('type') == 'Case Law':
                    ref_text += f"{i}. SHC Case {ref.get('case_no', 'N/A')}\n"
                elif ref.get('type') == 'CrPC':
                    ref_text += f"{i}. CrPC Section\n"
                elif ref.get('type') == 'Constitution':
                    ref_text += f"{i}. Constitution Article {ref.get('article', 'N/A')}\n"
        
        # Use improved prompts if available
        try:
            # Try importing from src directory
            try:
                from src.improved_prompts import build_stage2_prompt
            except ImportError:
                from improved_prompts import build_stage2_prompt
            
            prompt = build_stage2_prompt(
                question=question,
                initial_answer=initial_answer,
                context=context,
                references=references
            )
        except (ImportError, Exception) as e:
            # Fallback to original prompt if improved prompts not available
            print(f"   Note: Using default prompt (improved_prompts not available: {e})")
            # Enhanced fallback prompt that PRESERVES context information
            prompt = f"""You are an expert Pakistan criminal law assistant. Your task is to format and improve a legal answer while PRESERVING all correct legal information from the context.

CRITICAL RULE: The initial answer was generated using legal context. You MUST preserve any correct legal information from that context, especially about evidence priority, legal principles, and case citations.

ORIGINAL QUESTION: {question}

INITIAL ANSWER (needs improvement):
{initial_answer}

RELEVANT LEGAL CONTEXT (SOURCE OF INFORMATION):
{context[:1000]}

{ref_text}

CRITICAL TASKS:
1. PRESERVE all correct legal information from context (especially evidence priority rules)
2. If context says "ocular evidence has primacy" - KEEP that in your answer
3. If context contains case citations (PLD 2009 SC 45, 2020 SCMR 316, etc.) - INCLUDE them in your answer
4. Extract and include proper case citations from context (format: "PLD 2009 SC 45", "2020 SCMR 316")
5. Remove ALL prefixes like "For example:", "In this regard:", "Here,", etc.
6. Start directly with the answer - no introductory phrases
7. Complete any incomplete or cut-off sentences
8. Ensure the answer directly and clearly addresses the question
9. Format in a structured, professional manner
10. Maintain 100% legal accuracy - do NOT change any legal facts
11. Keep all section numbers, case names, and legal terms accurate
12. DO NOT remove context-based information - only improve formatting
13. If context mentions "PLD 2009 SC 45" or "2020 SCMR 316" - include these citations

REQUIRED FORMAT:
1. Direct Answer: Clear, concise answer (2-4 sentences) that directly addresses the question
2. Legal Basis: Relevant PPC/CrPC sections or Constitution articles (if applicable)
3. Key Details: Punishment, bail status, or other important information (if applicable)

STRICT RULES:
- Answer MUST be about Pakistan law ONLY (PPC, CrPC, Constitution)
- Do NOT mention US, UK, Indian (IPC), or Bangladesh law
- Do NOT add information not present in the initial answer
- Do NOT make up section numbers or case names
- Only improve structure, clarity, and completeness
- Keep all legal terminology accurate

FORMATTED ANSWER (start directly, no prefixes):"""

        try:
            # Use config if available
            config = PIPELINE_CONFIG.get("stage2", {})
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile"),
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are an expert Pakistan criminal law assistant. You format legal answers to be clear, complete, and professional. You NEVER add information not in the source, and you ALWAYS maintain legal accuracy."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": config.get("temperature", 0.3),
                    "max_tokens": config.get("max_tokens", 600),
                    "top_p": config.get("top_p", 0.9),
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                formatted = result['choices'][0]['message']['content'].strip()
                return formatted
            else:
                # Better error reporting
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get('error', {}).get('message', error_detail)
                except:
                    pass
                print(f"Groq API error {response.status_code}: {error_detail}")
                print("Falling back to initial answer (Stage 1 only)")
                return initial_answer
                
        except Exception as e:
            print(f"Error formatting with Groq: {e}")
            import traceback
            traceback.print_exc()
            return initial_answer
    
    def _format_with_huggingface(self, initial_answer: str, question: str, context: str, references: list) -> str:
        """Format answer using Hugging Face Inference API (FREE)"""
        
        prompt = f"""Format and improve this legal answer about Pakistan criminal law:

Question: {question}

Initial Answer:
{initial_answer}

Context:
{context[:800]}

Task: Format the answer clearly, remove "For example:" prefixes, complete sentences, and ensure it directly answers the question.

Formatted Answer:"""

        try:
            # Using Mistral 7B for formatting
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}" if self.formatter_api_key else None
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 400,
                        "temperature": 0.3,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    formatted = result[0].get('generated_text', initial_answer).strip()
                    return formatted
                return initial_answer
            else:
                print(f"Hugging Face API error: {response.status_code}")
                return initial_answer
                
        except Exception as e:
            print(f"Error formatting with Hugging Face: {e}")
            return initial_answer
    
    def _format_with_openai(self, initial_answer: str, question: str, context: str, references: list) -> str:
        """Format answer using OpenAI GPT-3.5 Turbo (PAID but CHEAP)"""
        
        prompt = f"""You are an expert legal text formatter. Improve and format this legal answer about Pakistan criminal law.

ORIGINAL QUESTION: {question}

INITIAL ANSWER (needs formatting):
{initial_answer}

RELEVANT CONTEXT:
{context[:1000]}

TASK:
1. Format the answer clearly and professionally
2. Remove any "For example:" or similar prefixes
3. Complete any incomplete sentences
4. Ensure direct answer to the question
5. Maintain all legal accuracy
6. Use structured format: Direct Answer → Legal Basis → Details

IMPORTANT:
- Keep ALL legal information accurate
- Do NOT add information not in the initial answer
- Only improve structure and clarity
- Answer must be about Pakistan law ONLY

FORMATTED ANSWER:"""

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an expert legal text formatter for Pakistan criminal law."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                formatted = result['choices'][0]['message']['content'].strip()
                return formatted
            else:
                print(f"OpenAI API error: {response.status_code}")
                return initial_answer
                
        except Exception as e:
            print(f"Error formatting with OpenAI: {e}")
            return initial_answer
    
    def generate_answer(self, question: str, use_formatter: bool = True) -> Dict:
        """
        Generate answer using two-stage pipeline
        
        Args:
            question: User question
            use_formatter: Whether to use Stage 2 formatter
        
        Returns:
            Dict with answer, references, timing, etc.
        """
        total_start = time.time()
        
        # Stage 1: Your model generates initial answer
        print("\n" + "=" * 60)
        print("STAGE 1: Retrieval + Initial Answer Generation")
        print("=" * 60)
        stage1_start = time.time()
        
        # Use optimized settings from config
        config = PIPELINE_CONFIG.get("stage1", {})
        
        stage1_result = self.stage1_model.generate_answer(
            question,
            max_new_tokens=config.get("max_new_tokens", 150),
            temperature=config.get("temperature", 0.2)
        )
        
        stage1_time = time.time() - stage1_start
        print(f"\nStage 1 complete in {stage1_time:.1f}s")
        print(f"Initial answer length: {len(stage1_result['answer'])} chars")
        
        # Stage 2: Formatting (if enabled)
        if use_formatter and self.use_formatter:
            print("\n" + "=" * 60)
            print("STAGE 2: Formatting & Improvement")
            print("=" * 60)
            stage2_start = time.time()
            
            # Get context from Stage 1
            context = ""
            if stage1_result.get('retrieved_docs'):
                context = "\n".join([
                    doc.get('text', '')[:200] 
                    for doc in stage1_result['retrieved_docs'][:3]
                ])
            
            # Format based on formatter type
            if self.formatter_type == "groq":
                formatted_answer = self._format_with_groq(
                    stage1_result['answer'],
                    question,
                    context,
                    stage1_result.get('references', [])
                )
            elif self.formatter_type == "huggingface":
                formatted_answer = self._format_with_huggingface(
                    stage1_result['answer'],
                    question,
                    context,
                    stage1_result.get('references', [])
                )
            elif self.formatter_type == "openai":
                formatted_answer = self._format_with_openai(
                    stage1_result['answer'],
                    question,
                    context,
                    stage1_result.get('references', [])
                )
            else:
                formatted_answer = stage1_result['answer']
            
            stage2_time = time.time() - stage2_start
            print(f"\nStage 2 complete in {stage2_time:.1f}s")
            print(f"Formatted answer length: {len(formatted_answer)} chars")
            
            final_answer = formatted_answer
        else:
            final_answer = stage1_result['answer']
            stage2_time = 0
        
        total_time = time.time() - total_start
        
        return {
            "question": question,
            "answer": final_answer,
            "initial_answer": stage1_result['answer'],  # For comparison
            "references": stage1_result.get('references', []),
            "context_used": stage1_result.get('context_used', False),
            "sources_count": stage1_result.get('sources_count', 0),
            "response_time": total_time,
            "stage1_time": stage1_time,
            "stage2_time": stage2_time,
            "formatted": use_formatter and self.use_formatter
        }

if __name__ == "__main__":
    # Example usage
    import sys
    
    # Check for API key
    formatter_type = "groq"  # Change to "huggingface", "openai", etc.
    api_key = os.getenv("GROQ_API_KEY")  # or OPENAI_API_KEY, etc.
    
    if not api_key and formatter_type in ["groq", "openai"]:
        print("WARNING: API key not found. Set GROQ_API_KEY or OPENAI_API_KEY environment variable")
        print("Continuing without formatter...")
    
    pipeline = TwoStagePipeline(
        peft_model_path="./models/final_model_v5",
        formatter_type=formatter_type,
        formatter_api_key=api_key
    )
    
    # Test
    question = "What is Section 302 PPC?"
    print(f"\nTesting with question: {question}")
    result = pipeline.generate_answer(question, use_formatter=True)
    
    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(f"\n{result['answer']}\n")
    print(f"Total time: {result['response_time']:.1f}s")
    print(f"  Stage 1: {result['stage1_time']:.1f}s")
    print(f"  Stage 2: {result['stage2_time']:.1f}s")
    print(f"Formatted: {result['formatted']}")

