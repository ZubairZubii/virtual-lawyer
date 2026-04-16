"""
Optimized Chatbot for Pakistan Criminal Law - Model v5
Fixes: Better prompt engineering, faster responses, structured answers
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import sys
import os
import time
import re

# Add project root and src to path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    from src.enhanced_rag_system import EnhancedRAGSystem as RAGSystem
except ImportError:
    from enhanced_rag_system import EnhancedRAGSystem as RAGSystem


class LegalChatbotV5:
    """Optimized chatbot with better prompt engineering and faster responses"""
    
    def __init__(self, 
                 base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                 peft_model_path="./models/final_model_v5",
                 use_rag=True):
        
        print("🤖 Initializing Legal Chatbot V5...")
        start_time = time.time()
        
        # Load tokenizer
        print("   📥 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Load base model (8-bit)
        print("   📥 Loading base model (8-bit)...")
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
        
        # Load LoRA weights
        print(f"   📥 Loading fine-tuned LoRA weights from {peft_model_path}...")
        self.model = PeftModel.from_pretrained(self.model, peft_model_path)
        self.model.eval()
        
        # Initialize RAG
        self.use_rag = use_rag
        if use_rag:
            print("   🧠 Initializing RAG system...")
            self.rag = RAGSystem()
            self.rag.load_corpus()
            self.rag.create_embeddings()
        
        load_time = time.time() - start_time
        print(f"✅ Chatbot ready! (Loaded in {load_time:.1f}s)\n")
    
    def _extract_section_number(self, question: str) -> str:
        """Extract PPC section number from question if mentioned"""
        match = re.search(r'Section\s+(\d+[A-Z]?)\s+PPC', question, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r'Section\s+(\d+[A-Z]?)', question, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _create_structured_prompt(self, question: str, context: str = "") -> str:
        """Create optimized prompt that forces structured, concise answers"""
        
        # Detect question type
        question_lower = question.lower()
        is_section_question = "section" in question_lower and ("ppc" in question_lower or "302" in question or "376" in question or "420" in question)
        is_punishment_question = "punishment" in question_lower or "sentence" in question_lower
        is_bail_question = "bail" in question_lower or "bailable" in question_lower
        is_rights_question = "right" in question_lower and ("arrest" in question_lower or "detention" in question_lower)
        
        # Build system instruction
        system_instruction = """You are an expert Pakistan criminal law assistant. Your role is to provide accurate, concise, and structured answers about Pakistan criminal law ONLY.

CRITICAL RULES:
1. Answer ONLY using Pakistan Penal Code (PPC), Code of Criminal Procedure (CrPC), and Constitution of Pakistan
2. NEVER mention US, UK, Indian (IPC), or Bangladesh law
3. Be concise: 3-5 sentences maximum for direct answer
4. Use structured format with clear sections
5. If you don't know, say "I don't have information about this specific aspect"
6. DO NOT copy-paste long case judgments - summarize key points only"""
        
        # Build context section
        context_section = ""
        if context:
            context_section = f"""RELEVANT LEGAL INFORMATION:
{context}

"""
        
        # Build answer format based on question type
        if is_section_question:
            section_num = self._extract_section_number(question)
            answer_format = f"""ANSWER FORMAT:
1. Definition: What is Section {section_num or 'this section'} PPC? (2-3 sentences)
2. Punishment: What is the punishment? (1-2 sentences)
3. Bailable: Is it bailable or non-bailable? (1 sentence)
4. Cognizable: Is it cognizable or non-cognizable? (1 sentence)"""
        elif is_punishment_question:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: What is the punishment? (2-3 sentences)
2. Section Reference: Relevant PPC section number
3. Details: Minimum/maximum punishment, fine if applicable"""
        elif is_bail_question:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: Is it bailable? (1-2 sentences)
2. Section Reference: Relevant PPC/CrPC section
3. Conditions: Any conditions for bail? (if applicable)"""
        elif is_rights_question:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: What are the rights? (3-4 sentences)
2. Legal Basis: Constitution/CrPC sections
3. Practical Steps: What should the person do?"""
        else:
            answer_format = """ANSWER FORMAT:
1. Direct Answer: (3-5 clear sentences)
2. Legal Basis: Relevant sections/laws
3. Additional Info: Important details (if applicable)"""
        
        # Combine into final prompt
        prompt = f"""{system_instruction}

{context_section}QUESTION: {question}

{answer_format}

Now provide your answer following the format above:"""
        
        return prompt
    
    def generate_response(self, question: str, max_new_tokens=256, temperature=0.3):
        """Generate optimized response with better prompt engineering"""
        
        start_time = time.time()
        
        # Step 1: RAG retrieval (optimized)
        context = ""
        retrieved_docs = []
        if self.use_rag:
            # Use fewer docs for faster retrieval
            retrieved_docs = self.rag.retrieve(question, top_k=2)
            if retrieved_docs:
                # Format context more concisely
                context_parts = []
                for doc in retrieved_docs[:2]:  # Max 2 docs
                    text = doc['text']
                    # Truncate long texts
                    if len(text) > 500:
                        text = text[:500] + "..."
                    context_parts.append(f"[{doc.get('source', 'unknown')}]: {text}")
                context = "\n\n".join(context_parts)
        
        # Step 2: Create optimized prompt
        prompt = self._create_structured_prompt(question, context)
        
        # Step 3: Tokenize (shorter max length for speed)
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024  # Reduced from 1800 for speed
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Step 4: Generate with optimized settings
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,  # Reduced for faster responses
                temperature=temperature,  # Lower temperature for more focused answers
                do_sample=True,
                top_p=0.85,  # Slightly lower for more focused
                top_k=40,  # Reduced for speed
                repetition_penalty=1.2,  # Increased to reduce repetition
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1,
                early_stopping=True  # Stop early if possible
            )
        
        # Step 5: Decode and extract answer
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract answer (improved extraction)
        answer = self._extract_answer(full_response, prompt, question)
        
        # Post-process answer
        answer = self._post_process_answer(answer)
        
        response_time = time.time() - start_time
        
        return {
            "question": question,
            "answer": answer,
            "context_used": bool(context),
            "retrieved_sources": len(retrieved_docs),
            "response_time": response_time
        }
    
    def _extract_answer(self, full_response: str, prompt: str, question: str) -> str:
        """Extract answer from model response"""
        
        # Try to find answer after prompt
        if prompt in full_response:
            answer = full_response.split(prompt, 1)[-1].strip()
        else:
            # Try common markers
            markers = [
                "Now provide your answer following the format above:",
                "ANSWER:",
                "Answer:",
                "A:",
            ]
            answer = full_response
            for marker in markers:
                if marker in full_response:
                    parts = full_response.split(marker, 1)
                    if len(parts) > 1:
                        answer = parts[-1].strip()
                        break
        
        # Remove question if it appears in answer
        if question in answer:
            answer = answer.split(question)[-1].strip()
        
        # Remove any remaining prompt artifacts
        lines = answer.split('\n')
        clean_lines = []
        skip_next = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip lines that look like prompts
            if any(x in line.lower() for x in ['question:', 'answer format:', 'legal context:', 'relevant legal']):
                continue
            # Stop at next question
            if line.lower().startswith('question:') or line.lower().startswith('q:'):
                break
            clean_lines.append(line)
        
        answer = '\n'.join(clean_lines).strip()
        
        # If answer is too short, try to get more
        if len(answer.split()) < 15:
            # Try to get more from full response
            lines = full_response.split('\n')
            capturing = False
            answer_lines = []
            
            for line in lines:
                line_lower = line.lower()
                if any(marker in line_lower for marker in ['answer:', 'definition:', 'punishment:', 'bailable:']):
                    capturing = True
                if capturing and line.strip():
                    if line.lower().startswith('question:'):
                        break
                    if not any(x in line.lower() for x in ['format', 'instruction', 'rule', 'critical']):
                        answer_lines.append(line.strip())
            
            if answer_lines:
                answer = '\n'.join(answer_lines).strip()
        
        return answer if answer else "I apologize, I could not generate a proper response. Please try rephrasing your question."
    
    def _post_process_answer(self, answer: str) -> str:
        """Post-process answer to improve quality"""
        
        # Remove excessive whitespace
        answer = re.sub(r'\s+', ' ', answer)
        answer = re.sub(r'\n\s*\n', '\n\n', answer)
        
        # Remove common artifacts
        artifacts = [
            "Answer based on Pakistani law.",
            "Based on the provided context",
            "According to Pakistan Penal Code",
        ]
        for artifact in artifacts:
            answer = answer.replace(artifact, "").strip()
        
        # Limit length (prevent rambling)
        sentences = answer.split('.')
        if len(sentences) > 15:  # Too long
            answer = '. '.join(sentences[:15]) + '.'
        
        return answer.strip()
    
    def chat(self):
        """Interactive chat mode"""
        print("=" * 60)
        print("PAKISTAN CRIMINAL LAW CHATBOT - V5")
        print("=" * 60)
        print("Type 'exit' to quit\n")
        
        while True:
            question = input("You: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\n🤔 Thinking...")
            response = self.generate_response(question)
            
            print(f"\n💡 Answer ({response['response_time']:.1f}s):")
            print(f"{response['answer']}\n")
            print(f"[Context: {'Yes' if response['context_used'] else 'No'} | Sources: {response['retrieved_sources']}]\n")
            print("-" * 60 + "\n")


if __name__ == "__main__":
    chatbot = LegalChatbotV5(
        peft_model_path="./models/final_model_v5",
        use_rag=True
    )
    chatbot.chat()























