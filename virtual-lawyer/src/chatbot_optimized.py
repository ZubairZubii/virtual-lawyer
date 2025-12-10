import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from rag import RAGSystem
import time

class OptimizedLegalChatbot:
    def __init__(self, 
                 base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                 peft_model_path="./models/fine-tuned/final_model",
                 use_rag=True):
        
        print("🤖 Initializing Optimized Legal Chatbot...")
        
        # Better quantization config
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False
        )
        
        # Load tokenizer
        print("   Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model with optimized settings
        print("   Loading model with optimizations...")
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=quantization_config,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        
        # Load LoRA weights
        print(f"   Loading LoRA weights from {peft_model_path}...")
        self.model = PeftModel.from_pretrained(self.model, peft_model_path)
        self.model.eval()
        
        # REMOVED torch.compile() - causes segmentation fault on Windows
        # self.model = torch.compile(self.model, mode="reduce-overhead")
        
        # Initialize RAG
        self.use_rag = use_rag
        if use_rag:
            print("   Loading RAG system...")
            self.rag = RAGSystem()
            self.rag.load_corpus()
            self.rag.create_embeddings()
        
        print("✅ Optimized Chatbot ready!\n")
    
    def generate_response(self, question, max_new_tokens=256, temperature=0.3):
        """Faster response generation"""
        start_time = time.time()
        
        # Step 1: RAG retrieval
        context = ""
        retrieved_docs = []
        if self.use_rag:
            retrieved_docs = self.rag.retrieve(question, top_k=2)
            context = self.rag.format_context(retrieved_docs, max_length=800)
        
        # Jurisdictional system instruction
        system_instr = (
            "You are an expert Pakistani criminal law assistant. "
            "Always answer strictly under Pakistan law (PPC and CrPC), with references to sections where applicable. "
            "Never reference U.S., U.K., Indian law (IPC) or any foreign jurisdiction. "
            "If the user is ambiguous, assume jurisdiction is Pakistan."
        )
        
        # Step 2: Create concise prompt
        if context:
            prompt = f"""{system_instr}

Context: {context}

Q: {question}
Final Answer:"""
        else:
            prompt = f"{system_instr}\n\nQ: {question}\nFinal Answer:"
        
        # Step 3: Tokenize
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Step 4: Generate with optimizations
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                num_beams=1,
                early_stopping=True
            )
        
        # Step 5: Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract answer using robust delimiters
        delimiters = ["Final Answer:", "Answer (Pakistan law ONLY):", "Answer (Pakistani law):", "Answer:", "A:"]
        answer = response
        for d in delimiters:
            if d in response:
                answer = response.split(d)[-1].strip()
        
        # Simple jurisdiction check; retry once if foreign jurisdictions are detected
        forbidden_terms = ["U.S.", "United States", "USA", "United Kingdom", "U.K.", "UK", "Indian Penal Code", "IPC"]
        if any(term.lower() in answer.lower() for term in forbidden_terms):
            reinforce = (
                "IMPORTANT: Only reference Pakistan Penal Code (PPC) and Code of Criminal Procedure (CrPC) of Pakistan. "
                "Do not reference any foreign law."
            )
            retry_prompt = f"""{system_instr}
{reinforce}

Q: {question}
Final Answer:"""
            retry_inputs = self.tokenizer(
                retry_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )
            retry_inputs = {k: v.to(self.model.device) for k, v in retry_inputs.items()}
            with torch.no_grad():
                retry_outputs = self.model.generate(
                    **retry_inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.2,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_beams=1,
                    early_stopping=True
                )
            retry_resp = self.tokenizer.decode(retry_outputs[0], skip_special_tokens=True)
            retry_answer = retry_resp
            for d in delimiters:
                if d in retry_resp:
                    retry_answer = retry_resp.split(d)[-1].strip()
            answer = retry_answer
        
        elapsed_time = time.time() - start_time
        
        return {
            "question": question,
            "answer": answer,
            "context_used": bool(context),
            "retrieved_sources": len(retrieved_docs),
            "response_time": round(elapsed_time, 2)
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
            print(f"[Time: {response['response_time']}s | Sources: {response['retrieved_sources']}]\n")
            print("-"*60 + "\n")

if __name__ == "__main__":
    chatbot = OptimizedLegalChatbot()
    chatbot.chat()