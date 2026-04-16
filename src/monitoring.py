import json
import os
from datetime import datetime
from typing import List, Dict
import pandas as pd

class ResponseMonitor:
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.conversations_file = os.path.join(log_dir, "conversations.json")
        self.conversations = self._load_conversations()
        
        self.flags = {
            "low_confidence": 0,
            "irrelevant_context": 0,
            "long_response_time": 0,
            "user_reported": 0
        }
    
    def _load_conversations(self):
        """Load existing conversations"""
        if os.path.exists(self.conversations_file):
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_conversations(self):
        """Save conversations to file"""
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
    
    def log_conversation(self, question, answer, context_used, sources_count, 
                        response_time, session_id):
        """Log a conversation with auto-flagging"""
        
        conversation = {
            "id": len(self.conversations) + 1,
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "context_used": context_used,
            "sources_count": sources_count,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "flagged": False,
            "flag_reasons": []
        }
        
        # Auto-flagging logic
        
        # Flag 1: No context used when RAG is enabled
        if not context_used and sources_count == 0:
            conversation["flagged"] = True
            conversation["flag_reasons"].append("No legal sources found")
            self.flags["irrelevant_context"] += 1
        
        # Flag 2: Very short answer (likely incomplete)
        if len(answer.split()) < 10:
            conversation["flagged"] = True
            conversation["flag_reasons"].append("Answer too short")
            self.flags["low_confidence"] += 1
        
        # Flag 3: Slow response time
        if response_time > 10:  # seconds
            conversation["flagged"] = True
            conversation["flag_reasons"].append(f"Slow response: {response_time}s")
            self.flags["long_response_time"] += 1
        
        # Flag 4: Answer contains uncertainty phrases
        uncertainty_phrases = ["i don't know", "i'm not sure", "might be", "possibly"]
        if any(phrase in answer.lower() for phrase in uncertainty_phrases):
            conversation["flagged"] = True
            conversation["flag_reasons"].append("Uncertain response")
            self.flags["low_confidence"] += 1
        
        self.conversations.append(conversation)
        self._save_conversations()
        
        return conversation
    
    def get_statistics(self):
        """Calculate monitoring statistics"""
        total = len(self.conversations)
        
        if total == 0:
            return {
                "total_queries": 0,
                "flagged_count": 0,
                "flag_rate": 0,
                "avg_response_time": 0,
                "rag_usage_rate": 0
            }
        
        flagged = sum(1 for c in self.conversations if c.get("flagged", False))
        total_time = sum(c.get("response_time", 0) for c in self.conversations)
        rag_used = sum(1 for c in self.conversations if c.get("context_used", False))
        
        # Query categories
        categories = {
            "bail": sum(1 for c in self.conversations if "bail" in c["question"].lower()),
            "fir": sum(1 for c in self.conversations if "fir" in c["question"].lower()),
            "arrest": sum(1 for c in self.conversations if "arrest" in c["question"].lower()),
            "rights": sum(1 for c in self.conversations if "rights" in c["question"].lower()),
            "section": sum(1 for c in self.conversations if "section" in c["question"].lower()),
        }
        
        return {
            "total_queries": total,
            "flagged_count": flagged,
            "flag_rate": round((flagged / total) * 100, 1),
            "avg_response_time": round(total_time / total, 2),
            "rag_usage_rate": round((rag_used / total) * 100, 1),
            "query_categories": categories,
            "flags_by_type": self.flags
        }
    
    def get_flagged_conversations(self):
        """Get all flagged conversations for review"""
        return [c for c in self.conversations if c.get("flagged", False)]
    
    def get_recent_conversations(self, limit=20):
        """Get recent conversations"""
        return sorted(
            self.conversations, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:limit]
    
    def export_to_csv(self, output_path="./logs/conversations_export.csv"):
        """Export conversations to CSV for analysis"""
        if not self.conversations:
            print("No conversations to export")
            return
        
        df = pd.DataFrame(self.conversations)
        df.to_csv(output_path, index=False)
        print(f"✅ Exported {len(df)} conversations to {output_path}")