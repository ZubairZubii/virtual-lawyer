"""
Master Script: Run Complete 5-Phase Improvement
Runs all processing steps in correct order
"""
import subprocess
import sys
from pathlib import Path

def run_step(step_name: str, script_path: str):
    """Run a processing step"""
    print("\n" + "=" * 60)
    print(f"STEP: {step_name}")
    print("=" * 60)
    
    script = Path(script_path)
    if not script.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {step_name} completed successfully")
            return True
        else:
            print(f"❌ {step_name} failed with return code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running {step_name}: {e}")
        return False

def main():
    """Run all improvement steps"""
    print("=" * 60)
    print("COMPLETE 5-PHASE IMPROVEMENT PIPELINE")
    print("=" * 60)
    print("\nThis will:")
    print("1. Process new PDFs to RAG")
    print("2. Process structured data to RAG")
    print("3. Create golden training data")
    print("4. Merge all RAG corpus")
    print("5. Provide instructions for embeddings rebuild")
    print()
    
    input("Press Enter to start...")
    
    steps = [
        ("Process New PDFs", "process_new_pdfs_to_rag.py"),
        ("Process Structured Data", "process_structured_data_to_rag.py"),
        ("Create Golden Training Data", "create_golden_training_data.py"),
        ("Merge All RAG Corpus", "merge_all_rag_corpus.py"),
    ]
    
    results = {}
    
    for step_name, script_path in steps:
        success = run_step(step_name, script_path)
        results[step_name] = success
        
        if not success:
            print(f"\n⚠️  {step_name} failed. Continue anyway? (y/n): ", end='')
            choice = input().lower()
            if choice != 'y':
                print("\n❌ Pipeline stopped by user")
                return
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    
    for step_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Rebuild embeddings:")
    print("   python -c \"from src.enhanced_rag_system import EnhancedRAGSystem; rag = EnhancedRAGSystem(corpus_path='./data/processed/comprehensive_rag_corpus.json'); rag.load_corpus(); rag.create_embeddings(force_rebuild=True)\"")
    print("\n2. Update RAG system to use new corpus:")
    print("   Edit src/enhanced_rag_system.py: corpus_path = './data/processed/comprehensive_rag_corpus.json'")
    print("\n3. Integrate validator (see integrate_validator_example.py)")
    print("\n4. Update prompts (see COMPLETE_5_PHASE_IMPLEMENTATION.md)")
    print("\n5. Optional: Retrain model with golden training data")
    print("\n" + "=" * 60)
    print("✅ PROCESSING COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()





















