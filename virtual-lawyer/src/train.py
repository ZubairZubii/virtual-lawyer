    import os
    import json
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    import bitsandbytes as bnb

    class LegalLLMTrainer:
        def __init__(self, 
                    model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # or use "mosaicml/mpt-7b-instruct"
                    training_data_path="./data/processed/training_data.json",
                    output_dir="./models/fine-tuned"):
            
            self.model_name = model_name
            self.training_data_path = training_data_path
            self.output_dir = output_dir
            
            os.makedirs(output_dir, exist_ok=True)
        
        def load_model_and_tokenizer(self):
            """Load model in 8-bit for 6GB GPU"""
            print(f"🤖 Loading model: {self.model_name}")
            print("   ⚙️  Using 8-bit quantization for memory efficiency...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "right"
            
            # Load model in 8-bit
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                load_in_8bit=True,
                device_map="auto",
                torch_dtype=torch.float16
            )
            
            # Prepare for k-bit training
            self.model = prepare_model_for_kbit_training(self.model)
            
            print("✅ Model loaded successfully")
            print(f"   Model size: ~4GB in 8-bit")
            print(f"   Device: {next(self.model.parameters()).device}")
        
        def setup_lora(self):
            """Configure LoRA for parameter-efficient fine-tuning"""
            print("\n🔧 Setting up LoRA...")
            
            lora_config = LoraConfig(
                r=16,  # Rank
                lora_alpha=32,
                target_modules=["q_proj", "v_proj"],  # Which layers to adapt
                lora_dropout=0.05,
                bias="none",
                task_type="CAUSAL_LM"
            )
            
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()
            
            print("✅ LoRA configured")
        
        def prepare_dataset(self):
            """Load and prepare training dataset"""
            print(f"\n📚 Loading training data from {self.training_data_path}...")

            with open(self.training_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} training examples")

            # Format for training
            def format_example(example):
                text = example['prompt'] + example['completion']
                return {"text": text}

            formatted_data = [format_example(ex) for ex in data]

            # Create HuggingFace dataset
            dataset = Dataset.from_list(formatted_data)

            # Tokenize
            def tokenize_function(examples):
                return self.tokenizer(
                    examples["text"],
                    truncation=True,
                    max_length=512,
                    padding="max_length"
                )

            tokenized_dataset = dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=dataset.column_names
            )

            # Split into train/eval
            split = tokenized_dataset.train_test_split(test_size=0.1)
            self.train_dataset = split['train']
            self.eval_dataset = split['test']

            print(f"✅ Dataset prepared:")
            print(f"   Train: {len(self.train_dataset)} examples")
            print(f"   Eval: {len(self.eval_dataset)} examples")

            return self.train_dataset, self.eval_dataset

        
        def train(self, num_epochs=3, batch_size=1, gradient_accumulation_steps=4, resume_from_checkpoint=None):
            """Train the model"""
            print("\n🚀 Starting training...")
            print(f"   Epochs: {num_epochs}")
            print(f"   Batch size: {batch_size}")
            print(f"   Gradient accumulation: {gradient_accumulation_steps}")
            print(f"   Effective batch size: {batch_size * gradient_accumulation_steps}")
            
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                gradient_accumulation_steps=gradient_accumulation_steps,
                learning_rate=3e-4,
                fp16=True,
                logging_steps=10,
                eval_strategy="steps",
                eval_steps=50,
                save_steps=100,
                save_total_limit=3,
                load_best_model_at_end=True,
                report_to="none",
                optim="paged_adamw_8bit"
            )
            
            data_collator = DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm=False)
            
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=self.train_dataset,
                eval_dataset=self.eval_dataset,
                data_collator=data_collator
            )
            
            print("\n⏳ Resuming training from checkpoint..." if resume_from_checkpoint else "\n⏳ Training in progress...")
            
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
            
            print("\n✅ Training complete!")
            
            final_path = os.path.join(self.output_dir, "final_model")
            trainer.save_model(final_path)
            self.tokenizer.save_pretrained(final_path)
            
            print(f"✅ Model saved to: {final_path}")

        
        def run_full_pipeline(self):
            """Run complete training pipeline"""
            print("="*60)
            print("STARTING LLM FINE-TUNING PIPELINE")
            print("="*60)
            
            # 1. Load model
            self.load_model_and_tokenizer()
            
            # 2. Setup LoRA
            self.setup_lora()
            
            # 3. Prepare dataset
            self.prepare_dataset()
            
            # 4. Train
            # Path to the latest checkpoint
            checkpoint_path = "./models/fine-tuned/checkpoint-500"
            self.train(resume_from_checkpoint=checkpoint_path)

            
            print("\n" + "="*60)
            print("✅ FINE-TUNING COMPLETE!")
            print("="*60)

    if __name__ == "__main__":
        trainer = LegalLLMTrainer()
        trainer.run_full_pipeline()