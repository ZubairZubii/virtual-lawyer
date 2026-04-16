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

class MultiLayerPipeline:
    """Multi-layer pipeline for best answer generation"""
    
    def __init__(self,
                 base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                 peft_model_path="./models/final_model_v5",
                 use_rag=True):
        
        print("Initializing Multi-Layer Pipeline...")
        start_time = time.time()
        
        # Layer 1: Load Model
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
        
        # Layer 2: Initialize Multi-Source RAG
        if use_rag:
            print("\nLayer 2: Initializing Multi-Source RAG...")
            self.rag = MultiSourceRAG()
            print("   RAG system ready")
        else:
            self.rag = None
        
        load_time = time.time() - start_time
        print(f"\nPipeline ready! (Loaded in {load_time:.1f}s)\n")
    
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
        
        # Layer 1: RAG Retrieval
        context = ""
        references = []
        retrieved_docs = []
        
        if self.rag:
            retrieved_docs = self.rag.retrieve(question, top_k=5)
            context, references = self.rag.format_context_with_references(retrieved_docs, max_length=2500)
        
        # Layer 2: Create Enhanced Prompt
        prompt = self._create_enhanced_prompt(question, context, references)
        
        # Layer 3: Model Generation
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1200
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
                eos_token_id=self.tokenizer.eos_token_id,
                early_stopping=True
            )
        
        # Layer 4: Extract Answer
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = self._extract_answer(full_response, prompt)
        
        # Layer 5: Post-process and Add References
        answer = self._post_process_answer(answer)
        
        response_time = time.time() - start_time
        
        return {
            "question": question,
            "answer": answer,
            "references": references,
            "context_used": bool(context),
            "sources_count": len(retrieved_docs),
            "response_time": response_time,
            "retrieved_docs": retrieved_docs[:3]  # Top 3 for debugging
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

