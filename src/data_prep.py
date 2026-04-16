import json
import pandas as pd
from datasets import load_dataset
import re
from tqdm import tqdm

class DataProcessor:
    def __init__(self, raw_dir="./data/raw", processed_dir="./data/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
    
    def process_cases_instruct(self):
        """Process Cases-Instruct-pk for training"""
        print("🔄 Processing Cases-Instruct-pk...")
        
        # Load
        with open(f"{self.raw_dir}/cases_instruct_train_fixed.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format for training
        processed = []
        for item in tqdm(data):
            # Create prompt-completion pairs
            instruction = item.get('instruction', '')
            input_text = item.get('input', '')
            output = item.get('output', '')
            
            if instruction and output:
                # Format as Q&A
                question = instruction
                if input_text:
                    question += f"\n{input_text}"
                
                processed.append({
                    "prompt": f"Question: {question}\nAnswer:",
                    "completion": f" {output}",
                    "source": "cases_instruct"
                })
        
        # Save
        output_path = f"{self.processed_dir}/training_data.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processed {len(processed)} training examples")
        print(f"   Saved to: {output_path}")
        
        return processed
    
    def process_pakistan_laws(self):
        """Process Pakistan Laws Dataset for RAG"""
        print("\n🔄 Processing Pakistan Laws Dataset...")
        
        # Load
        with open(f"{self.raw_dir}/pakistan_laws.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract law sections
        corpus = []
        for item in tqdm(data):
            text = item.get('text', '')
            title = item.get('title', '')
            
            if text:
                # Split into chunks (500 words each)
                words = text.split()
                for i in range(0, len(words), 500):
                    chunk = ' '.join(words[i:i+500])
                    if len(chunk.split()) > 50:  # At least 50 words
                        corpus.append({
                            "text": chunk,
                            "title": title,
                            "source": "pakistan_laws"
                        })
        
        # Save
        output_path = f"{self.processed_dir}/rag_corpus.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created {len(corpus)} corpus chunks")
        print(f"   Saved to: {output_path}")
        
        return corpus
    
    def process_ppc_sections(self):
        """Process PPC PDF into structured sections"""
        print("\n🔄 Processing Pakistan Penal Code...")
        
        # Load extracted text
        with open(f"{self.raw_dir}/ppc_extracted.json", 'r', encoding='utf-8') as f:
            pages = json.load(f)
        
        # Combine all pages
        full_text = "\n".join([p['text'] for p in pages])
        
        # Try to extract sections (Section XXX: Title)
        section_pattern = r'(Section\s+\d+[A-Z]?[:\-].*?)(?=Section\s+\d+|$)'
        sections = re.findall(section_pattern, full_text, re.DOTALL | re.IGNORECASE)
        
        ppc_corpus = []
        for section in sections:
            section_clean = section.strip()
            if len(section_clean) > 100:  # Meaningful content
                ppc_corpus.append({
                    "text": section_clean,
                    "source": "ppc"
                })
        
        # Also split into general chunks
        words = full_text.split()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i+400])
            if len(chunk.split()) > 50:
                ppc_corpus.append({
                    "text": chunk,
                    "source": "ppc_chunk"
                })
        
        # Save
        output_path = f"{self.processed_dir}/ppc_corpus.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ppc_corpus, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Extracted {len(ppc_corpus)} PPC sections/chunks")
        print(f"   Saved to: {output_path}")
        
        return ppc_corpus
    
    def merge_corpus(self):
        """Merge all corpus for RAG"""
        print("\n🔄 Merging all corpus for RAG...")

        all_corpus = []
        files = ["rag_corpus.json", "ppc_corpus.json"]

        for file in files:
            path = f"{self.processed_dir}/{file}"
            try:
                with open(path, 'r', encoding='utf-8') as f:  # ✅ FIXED ENCODING
                    data = json.load(f)
                    all_corpus.extend(data)
                    print(f"   Loaded {len(data)} items from {file}")
            except FileNotFoundError:
                print(f"   ⚠️  {file} not found, skipping")
            except UnicodeDecodeError as e:
                print(f"   ❌ Unicode error reading {file}: {e}")
                continue

        # Save merged corpus
        output_path = f"{self.processed_dir}/full_rag_corpus.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_corpus, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Total RAG corpus: {len(all_corpus)} documents")
        print(f"   Saved to: {output_path}")

        return all_corpus

    
    def process_all(self):
        """Process all datasets"""
        print("="*60)
        print("PROCESSING ALL DATASETS")
        print("="*60)
        
        # Create output directory
        import os
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # 1. Training data
        training_data = self.process_cases_instruct()
        
        # 2. RAG corpus
        pakistan_laws = self.process_pakistan_laws()
        ppc_corpus = self.process_ppc_sections()
        
        # 3. Merge corpus
        full_corpus = self.merge_corpus()
        
        print("\n" + "="*60)
        print("✅ ALL PROCESSING COMPLETE")
        print(f"   Training examples: {len(training_data)}")
        print(f"   RAG corpus size: {len(full_corpus)}")
        print("="*60)
        
        return {
            'training_data': training_data,
            'rag_corpus': full_corpus
        }

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_all()