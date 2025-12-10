import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import sys
import os

# Add project root and src to path for imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Import RAG system
try:
    from src.enhanced_rag_system import EnhancedRAGSystem as RAGSystem
except ImportError:
    from enhanced_rag_system import EnhancedRAGSystem as RAGSystem



class LegalChatbot:
    def __init__(self, 
                 base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                 peft_model_path="./models/fine-tuned/final_model",
                 use_rag=True):
        
        print("🤖 Initializing Legal Chatbot...")
        
        # Load tokenizer
        print("   Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        print("   Loading base model (8-bit)...")
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
        print(f"   Loading fine-tuned LoRA weights from {peft_model_path}...")
        self.model = PeftModel.from_pretrained(self.model, peft_model_path)
        self.model.eval()
        
        # Initialize RAG
        self.use_rag = use_rag
        if use_rag:
            print("   Initializing RAG system...")
            self.rag = RAGSystem()
            self.rag.load_corpus()
            self.rag.create_embeddings()
        
        print("✅ Chatbot ready!\n")
    
    def generate_response(self, question, max_length=512, temperature=0.7):
        """Generate response with STRONG Pakistan law enforcement"""

        # Step 1: RAG retrieval
        context = ""
        retrieved_docs = []
        if self.use_rag:
            retrieved_docs = self.rag.retrieve(question, top_k=3)
            context = self.rag.format_context(retrieved_docs, max_length=1500)

        # Step 2: Create IMPROVED prompt with structure
        if context:
            prompt = f"""You are an expert Pakistan criminal lawyer. Answer accurately and concisely.

LEGAL CONTEXT:
    {context}

Question: {question}

Answer in this format:
1. Direct answer (2-3 clear sentences)
2. Relevant PPC section number (if applicable)
3. Punishment details (if applicable)
4. Bail status (if applicable)

    IMPORTANT:
- Use ONLY Pakistan Penal Code (PPC), CrPC, and Pakistan Constitution
- DO NOT mention US, UK, Indian, or Bangladesh law
- Be accurate - do not make up section numbers
- If unsure, say so

Answer:"""
        else:
            prompt = f"""You are an expert Pakistan criminal lawyer. Answer accurately.

Question: {question}

Answer in this format:
1. Direct answer (2-3 clear sentences)
2. Relevant PPC section number (if applicable)
3. Punishment details (if applicable)

IMPORTANT:
- Use ONLY Pakistan law
- Be accurate - do not make up information

Answer:"""

        # Step 3: Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1800)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # Step 4: Generate with better settings
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.15,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )

        # Step 5: Decode full response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Step 6: Extract ONLY the answer part (after the prompt)
        # Find where the actual answer starts
        answer_markers = [
            "Pakistan Law Answer:",
            "Answer:",
            "A:",
            f"{question}"  # Sometimes answer comes right after question
        ]
        
        answer = full_response
        for marker in answer_markers:
            if marker in full_response:
                parts = full_response.split(marker)
                if len(parts) > 1:
                    answer = parts[-1].strip()
                    break
        
        # Clean up the answer
        answer = answer.strip()
        
        # Remove any remaining prompt artifacts
        if answer.startswith("-"):
            answer = answer[1:].strip()
        
        # If answer is too short or looks wrong, try alternative extraction
        if len(answer.split()) < 10 or "Question:" in answer:
            # The model might have included the prompt in output
            # Try to find the actual answer content
            lines = full_response.split('\n')
            answer_lines = []
            capturing = False
            
            for line in lines:
                if any(marker in line for marker in answer_markers):
                    capturing = True
                    continue
                if capturing and line.strip():
                    # Stop if we hit another question
                    if "Question:" in line or "User Question:" in line:
                        break
                    answer_lines.append(line.strip())
            
            if answer_lines:
                answer = ' '.join(answer_lines)
        
        # Final cleanup
        answer = answer.replace("- Answer based on Pakistani law.", "").strip()
        answer = answer.split("Question:")[0].strip()  # Remove any trailing questions
        
        return {
            "question": question,
            "answer": answer if answer else "I apologize, I could not generate a proper response. Please try rephrasing your question.",
            "context_used": bool(context),
            "retrieved_sources": len(retrieved_docs)
        }


    def chat(self):
        """Interactive chat mode"""
        print("="*60)
        print("LEGAL CHATBOT - Interactive Mode")
        print("Type 'exit' to quit")
        print("="*60 + "\n")
        
        while True:
            question = input("You: ")
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question.strip():
                continue
            
            print("\nBot: Thinking...\n")
            response = self.generate_response(question)
            
            print(f"Bot: {response['answer']}\n")
            print(f"[Context used: {response['context_used']}, Sources: {response['retrieved_sources']}]\n")
            print("-"*60 + "\n")

# Test the chatbot
if __name__ == "__main__":
    chatbot = LegalChatbot()
    chatbot.chat()