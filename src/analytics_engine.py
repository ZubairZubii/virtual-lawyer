import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List
import re

class AdvancedAnalytics:
    """Advanced analytics for legal chatbot - trends, insights, predictions"""
    
    def __init__(self, logs_dir="./logs", data_dir="./data/analytics"):
        self.logs_dir = logs_dir
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.response_log = os.path.join(logs_dir, "responses.jsonl")
    
    def get_comprehensive_stats(self, days: int = 30) -> Dict:
        """Get comprehensive statistics for dashboard"""
        
        if not os.path.exists(self.response_log):
            return self._empty_stats()
        
        logs = self._load_logs(days)
        
        if not logs:
            return self._empty_stats()
        
        stats = {
            "overview": self._get_overview_stats(logs),
            "trends": self._get_trends(logs),
            "popular_topics": self._get_popular_topics(logs),
            "performance": self._get_performance_metrics(logs),
            "quality_insights": self._get_quality_insights(logs),
            "usage_patterns": self._get_usage_patterns(logs),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to file
        stats_file = os.path.join(self.data_dir, "latest_stats.json")
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def _load_logs(self, days: int = None) -> List[Dict]:
        """Load logs from file, optionally filtered by days"""
        logs = []
        cutoff_date = None
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
        
        with open(self.response_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log = json.loads(line)
                    
                    if cutoff_date:
                        log_time = datetime.fromisoformat(log.get('timestamp', ''))
                        if log_time < cutoff_date:
                            continue
                    
                    logs.append(log)
                except:
                    continue
        
        return logs
    
    def _get_overview_stats(self, logs: List[Dict]) -> Dict:
        """Get overview statistics"""
        total = len(logs)
        
        rag_used = sum(1 for log in logs if log.get('context_used', False))
        
        total_response_time = sum(log.get('response_time', 0) for log in logs)
        avg_response_time = total_response_time / total if total > 0 else 0
        
        quality_counts = Counter(log.get('metrics', {}).get('response_quality', 'unknown') 
                                for log in logs)
        
        total_sources = sum(log.get('sources_count', 0) for log in logs)
        
        return {
            "total_queries": total,
            "rag_usage_rate": round((rag_used / total) * 100, 1) if total > 0 else 0,
            "avg_response_time": round(avg_response_time, 2),
            "total_sources_retrieved": total_sources,
            "quality_breakdown": {
                "excellent": quality_counts.get('excellent', 0),
                "good": quality_counts.get('good', 0),
                "fair": quality_counts.get('fair', 0),
                "poor": quality_counts.get('poor', 0)
            },
            "unique_sessions": len(set(log.get('session_id', '') for log in logs))
        }
    
    def _get_trends(self, logs: List[Dict]) -> Dict:
        """Analyze trends over time"""
        
        # Group by date
        daily_counts = defaultdict(int)
        daily_quality = defaultdict(list)
        
        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log.get('timestamp', ''))
                date_key = timestamp.strftime('%Y-%m-%d')
                
                daily_counts[date_key] += 1
                
                quality = log.get('metrics', {}).get('quality_score', 0)
                daily_quality[date_key].append(quality)
            except:
                continue
        
        # Convert to chart data
        sorted_dates = sorted(daily_counts.keys())
        
        query_trend = [
            {"date": date, "count": daily_counts[date]} 
            for date in sorted_dates
        ]
        
        quality_trend = [
            {
                "date": date, 
                "avg_quality": round(sum(daily_quality[date]) / len(daily_quality[date]), 2)
            }
            for date in sorted_dates if date in daily_quality
        ]
        
        return {
            "query_volume": query_trend[-14:],  # Last 14 days
            "quality_trend": quality_trend[-14:]
        }
    
    def _get_popular_topics(self, logs: List[Dict]) -> List[Dict]:
        """Identify most queried topics"""
        
        # Extract sections and keywords
        section_counts = Counter()
        keyword_counts = Counter()
        
        legal_keywords = [
            'murder', 'theft', 'bail', 'fir', 'arrest', 'court', 
            'evidence', 'trial', 'punishment', 'fine', 'imprisonment',
            'accused', 'witness', 'lawyer', 'advocate'
        ]
        
        for log in logs:
            question = log.get('question', '').lower()
            
            # Extract sections
            sections = re.findall(r'\b(section\s+\d{2,3}[a-z]?|§\s*\d{2,3})\b', question, re.IGNORECASE)
            for sec in sections:
                section_counts[sec] += 1
            
            # Count keywords
            for keyword in legal_keywords:
                if keyword in question:
                    keyword_counts[keyword] += 1
        
        return {
            "top_sections": [
                {"section": sec, "count": count} 
                for sec, count in section_counts.most_common(10)
            ],
            "top_keywords": [
                {"keyword": kw, "count": count}
                for kw, count in keyword_counts.most_common(15)
            ]
        }
    
    def _get_performance_metrics(self, logs: List[Dict]) -> Dict:
        """Get performance metrics"""
        
        response_times = [log.get('response_time', 0) for log in logs]
        
        if not response_times:
            return {}
        
        response_times_sorted = sorted(response_times)
        n = len(response_times_sorted)
        
        return {
            "avg_response_time": round(sum(response_times) / n, 2),
            "median_response_time": round(response_times_sorted[n // 2], 2),
            "p95_response_time": round(response_times_sorted[int(n * 0.95)], 2),
            "min_response_time": round(min(response_times), 2),
            "max_response_time": round(max(response_times), 2),
            "fast_responses": sum(1 for t in response_times if t < 2.0),
            "slow_responses": sum(1 for t in response_times if t > 5.0)
        }
    
    def _get_quality_insights(self, logs: List[Dict]) -> Dict:
        """Get quality insights"""
        
        quality_scores = []
        toxic_count = 0
        incomplete_count = 0
        
        for log in logs:
            metrics = log.get('metrics', {})
            
            quality_scores.append(metrics.get('quality_score', 0))
            
            if metrics.get('toxicity_score', 0) > 0:
                toxic_count += 1
            
            if metrics.get('completeness_score', 0) < 2:
                incomplete_count += 1
        
        total = len(logs)
        
        return {
            "avg_quality_score": round(sum(quality_scores) / total, 2) if total > 0 else 0,
            "toxic_responses_count": toxic_count,
            "toxic_rate": round((toxic_count / total) * 100, 2) if total > 0 else 0,
            "incomplete_responses": incomplete_count,
            "answers_with_legal_terms": sum(1 for log in logs 
                                           if log.get('metrics', {}).get('has_legal_terms', False)),
            "context_usage_effectiveness": self._calculate_context_effectiveness(logs)
        }
    
    def _calculate_context_effectiveness(self, logs: List[Dict]) -> float:
        """Calculate how effective RAG context is"""
        
        with_context = [log for log in logs if log.get('context_used', False)]
        without_context = [log for log in logs if not log.get('context_used', False)]
        
        if not with_context:
            return 0.0
        
        avg_quality_with = sum(log.get('metrics', {}).get('quality_score', 0) 
                              for log in with_context) / len(with_context)
        
        if not without_context:
            return round(avg_quality_with, 2)
        
        avg_quality_without = sum(log.get('metrics', {}).get('quality_score', 0) 
                                 for log in without_context) / len(without_context)
        
        improvement = ((avg_quality_with - avg_quality_without) / avg_quality_without) * 100
        
        return round(improvement, 1)
    
    def _get_usage_patterns(self, logs: List[Dict]) -> Dict:
        """Analyze usage patterns"""
        
        hour_counts = defaultdict(int)
        session_query_counts = defaultdict(int)
        
        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log.get('timestamp', ''))
                hour = timestamp.hour
                hour_counts[hour] += 1
                
                session_id = log.get('session_id', 'unknown')
                session_query_counts[session_id] += 1
            except:
                continue
        
        # Find peak hours
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Session analysis
        queries_per_session = list(session_query_counts.values())
        avg_queries_per_session = sum(queries_per_session) / len(queries_per_session) if queries_per_session else 0
        
        return {
            "peak_hours": [
                {"hour": f"{hour:02d}:00", "queries": count}
                for hour, count in peak_hours
            ],
            "avg_queries_per_session": round(avg_queries_per_session, 1),
            "total_sessions": len(session_query_counts),
            "hourly_distribution": [
                {"hour": hour, "count": hour_counts.get(hour, 0)}
                for hour in range(24)
            ]
        }
    
    def _empty_stats(self) -> Dict:
        """Return empty stats structure"""
        return {
            "overview": {},
            "trends": {},
            "popular_topics": {},
            "performance": {},
            "quality_insights": {},
            "usage_patterns": {},
            "error": "No data available",
            "generated_at": datetime.now().isoformat()
        }
    
    def export_report(self, output_path: str = None) -> str:
        """Export analytics report as JSON"""
        
        stats = self.get_comprehensive_stats()
        
        if not output_path:
            output_path = os.path.join(self.data_dir, f"report_{datetime.now().strftime('%Y%m%d')}.json")
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return output_path

if __name__ == "__main__":
    analytics = AdvancedAnalytics()
    
    print("📊 Generating comprehensive analytics...")
    stats = analytics.get_comprehensive_stats()
    
    print("\n" + "="*60)
    print("ANALYTICS REPORT")
    print("="*60)
    print(json.dumps(stats, indent=2))
    
    # Export report
    report_path = analytics.export_report()
    print(f"\n✅ Report exported to: {report_path}")