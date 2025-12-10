import os
from datasets import load_dataset
import requests
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
import json

class DatasetDownloader:
    def __init__(self, data_dir="./data/raw"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def download_cases_instruct(self):
        """Download Cases-Instruct-pk dataset"""
        print("📥 Downloading Cases-Instruct-pk...")
        
        try:
            dataset = load_dataset("mahwizzzz/Cases-Instruct-pk")
            
            # Save to JSON
            train_path = os.path.join(self.data_dir, "cases_instruct_train.json")
            dataset['train'].to_json(train_path)
            
            print(f"✅ Downloaded {len(dataset['train'])} training examples")
            print(f"   Saved to: {train_path}")
            
            # Preview
            print("\n📄 Sample:")
            print(dataset['train'][0])
            
            return dataset
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def download_pakistan_laws(self):
        """Download Pakistan Laws Dataset"""
        print("\n📥 Downloading Pakistan Laws Dataset...")
        
        try:
            dataset = load_dataset("AyeshaJadoon/Pakistan_Laws_Dataset")
            
            # Save to JSON
            laws_path = os.path.join(self.data_dir, "pakistan_laws.json")
            dataset['train'].to_json(laws_path)
            
            print(f"✅ Downloaded {len(dataset['train'])} law documents")
            print(f"   Saved to: {laws_path}")
            
            return dataset
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def download_ppc_pdf(self):
        """Download Pakistan Penal Code PDF"""
        print("\n📥 Downloading Pakistan Penal Code PDF...")
        
        url = "https://legal-tools.org/doc/073306/pdf"
        pdf_path = os.path.join(self.data_dir, "pakistan_penal_code.pdf")
        
        try:
            response = requests.get(url, timeout=30)
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded PPC PDF")
            print(f"   Saved to: {pdf_path}")
            
            return pdf_path
        except Exception as e:
            print(f"❌ Error downloading PDF: {e}")
            return None
    
    def extract_ppc_text(self, pdf_path):
        """Extract text from PPC PDF"""
        print("\n📖 Extracting text from PPC PDF...")
        
        if not os.path.exists(pdf_path):
            print("❌ PDF not found!")
            return None
        
        try:
            text_data = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_data.append({
                            "page": i + 1,
                            "text": text.strip()
                        })
            
            # Save extracted text
            text_path = os.path.join(self.data_dir, "ppc_extracted.json")
            with open(text_path, 'w', encoding='utf-8') as f:
                json.dump(text_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Extracted {len(text_data)} pages")
            print(f"   Saved to: {text_path}")
            
            return text_data
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return None
    
    def download_all(self):
        """Download all datasets"""
        print("="*60)
        print("DOWNLOADING ALL DATASETS")
        print("="*60)
        
        # 1. Cases Instruct
        cases_dataset = self.download_cases_instruct()
        
        # 2. Pakistan Laws
        laws_dataset = self.download_pakistan_laws()
        
        # 3. PPC PDF
        ppc_path = self.download_ppc_pdf()
        if ppc_path:
            self.extract_ppc_text(ppc_path)
        
        print("\n" + "="*60)
        print("✅ ALL DOWNLOADS COMPLETE")
        print("="*60)
        
        return {
            'cases_instruct': cases_dataset,
            'pakistan_laws': laws_dataset,
            'ppc_pdf': ppc_path
        }

if __name__ == "__main__":
    downloader = DatasetDownloader()
    downloader.download_all()