import json
import os
from datetime import datetime, timedelta
import random
from collections import defaultdict

class CaseAnalytics:
    def __init__(self, data_file="./logs/analytics_data.json"):
        self.data_file = data_file
        self.cases = self._load_or_generate_data()
    
    def _load_or_generate_data(self):
        """Load existing data or generate sample data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        
        # Generate sample data for demonstration
        return self._generate_sample_cases()
    
    def _generate_sample_cases(self):
        """Generate realistic sample case data"""
        crimes = ["theft", "fraud", "assault", "robbery", "cheating", "forgery"]
        outcomes = ["won", "lost", "pending"]
        
        cases = []
        for i in range(50):
            days_ago = random.randint(1, 365)
            outcome = random.choice(outcomes)
            
            case = {
                "id": f"CASE-2024-{i+1:03d}",
                "crime_type": random.choice(crimes),
                "filing_date": (datetime.now() - timedelta(days=days_ago)).isoformat(),
                "outcome": outcome,
                "duration_days": random.randint(30, 300) if outcome != "pending" else None,
                "lawyer_experience": random.randint(1, 15),
                "client_satisfied": random.choice([True, False]) if outcome != "pending" else None,
                "bail_granted": random.choice([True, False, None]),
                "risk_score": random.randint(20, 90)
            }
            cases.append(case)
        
        # Save generated data
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(cases, f, indent=2)
        
        return cases
    
    def get_performance_metrics(self):
        """Calculate overall performance metrics"""
        total_cases = len(self.cases)
        closed_cases = [c for c in self.cases if c["outcome"] != "pending"]
        active_cases = total_cases - len(closed_cases)
        
        won_cases = sum(1 for c in closed_cases if c["outcome"] == "won")
        lost_cases = sum(1 for c in closed_cases if c["outcome"] == "lost")
        
        win_rate = (won_cases / len(closed_cases) * 100) if closed_cases else 0
        
        # Average case duration
        durations = [c["duration_days"] for c in closed_cases if c["duration_days"]]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Client satisfaction
        satisfied = sum(1 for c in closed_cases if c.get("client_satisfied", False))
        satisfaction_rate = (satisfied / len(closed_cases) * 100) if closed_cases else 0
        
        # Bail success rate
        bail_granted = sum(1 for c in self.cases if c.get("bail_granted", False))
        bail_applied = sum(1 for c in self.cases if c.get("bail_granted") is not None)
        bail_success_rate = (bail_granted / bail_applied * 100) if bail_applied else 0
        
        return {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "closed_cases": len(closed_cases),
            "won_cases": won_cases,
            "lost_cases": lost_cases,
            "win_rate": round(win_rate, 1),
            "avg_case_duration_days": round(avg_duration, 0),
            "client_satisfaction_rate": round(satisfaction_rate, 1),
            "bail_success_rate": round(bail_success_rate, 1)
        }
    
    def get_monthly_trends(self, months=6):
        """Get monthly performance trends"""
        monthly_data = defaultdict(lambda: {"won": 0, "lost": 0, "filed": 0})
        
        for case in self.cases:
            filing_date = datetime.fromisoformat(case["filing_date"])
            month_key = filing_date.strftime("%Y-%m")
            
            monthly_data[month_key]["filed"] += 1
            
            if case["outcome"] == "won":
                monthly_data[month_key]["won"] += 1
            elif case["outcome"] == "lost":
                monthly_data[month_key]["lost"] += 1
        
        # Convert to list and sort
        result = []
        for month, data in sorted(monthly_data.items())[-months:]:
            total = data["won"] + data["lost"]
            win_rate = (data["won"] / total * 100) if total > 0 else 0
            
            result.append({
                "month": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
                "cases_filed": data["filed"],
                "cases_won": data["won"],
                "cases_lost": data["lost"],
                "win_rate": round(win_rate, 1)
            })
        
        return result
    
    def get_crime_type_analysis(self):
        """Analyze performance by crime type"""
        crime_stats = defaultdict(lambda: {"total": 0, "won": 0, "pending": 0, "risk_scores": []})
        
        for case in self.cases:
            crime = case["crime_type"]
            crime_stats[crime]["total"] += 1
            crime_stats[crime]["risk_scores"].append(case.get("risk_score", 50))
            
            if case["outcome"] == "won":
                crime_stats[crime]["won"] += 1
            elif case["outcome"] == "pending":
                crime_stats[crime]["pending"] += 1
        
        result = []
        for crime, stats in crime_stats.items():
            closed = stats["total"] - stats["pending"]
            success_rate = (stats["won"] / closed * 100) if closed > 0 else 0
            avg_risk = sum(stats["risk_scores"]) / len(stats["risk_scores"])
            
            result.append({
                "crime_type": crime.title(),
                "total_cases": stats["total"],
                "won": stats["won"],
                "pending": stats["pending"],
                "success_rate": round(success_rate, 1),
                "avg_risk_score": round(avg_risk, 1)
            })
        
        return sorted(result, key=lambda x: x["total_cases"], reverse=True)
    
    def get_urgent_alerts(self):
        """Identify cases requiring immediate attention"""
        alerts = []
        
        for case in self.cases:
            if case["outcome"] != "pending":
                continue
            
            filing_date = datetime.fromisoformat(case["filing_date"])
            days_pending = (datetime.now() - filing_date).days
            
            # High urgency criteria
            if days_pending > 180:
                alerts.append({
                    "case_id": case["id"],
                    "crime_type": case["crime_type"].title(),
                    "days_pending": days_pending,
                    "urgency": "CRITICAL",
                    "message": f"Case pending for {days_pending} days - IMMEDIATE ACTION REQUIRED",
                    "risk_score": case.get("risk_score", 50)
                })
            elif days_pending > 90:
                alerts.append({
                    "case_id": case["id"],
                    "crime_type": case["crime_type"].title(),
                    "days_pending": days_pending,
                    "urgency": "HIGH",
                    "message": f"Case pending for {days_pending} days - follow-up recommended",
                    "risk_score": case.get("risk_score", 50)
                })
            elif case.get("risk_score", 50) > 75:
                alerts.append({
                    "case_id": case["id"],
                    "crime_type": case["crime_type"].title(),
                    "days_pending": days_pending,
                    "urgency": "HIGH",
                    "message": f"High-risk case (score: {case.get('risk_score')}) - expert review needed",
                    "risk_score": case.get("risk_score", 50)
                })
        
        return sorted(alerts, key=lambda x: (x["urgency"] == "CRITICAL", x["days_pending"]), reverse=True)
    
    def get_lawyer_performance_insights(self):
        """Analyze lawyer performance based on experience"""
        experienced_cases = [c for c in self.cases if c["lawyer_experience"] > 5]
        novice_cases = [c for c in self.cases if c["lawyer_experience"] <= 5]
        
        def calc_win_rate(cases):
            closed = [c for c in cases if c["outcome"] in ["won", "lost"]]
            won = sum(1 for c in closed if c["outcome"] == "won")
            return (won / len(closed) * 100) if closed else 0
        
        exp_win_rate = calc_win_rate(experienced_cases)
        nov_win_rate = calc_win_rate(novice_cases)
        
        return {
            "experienced_lawyers": {
                "experience_years": "5+",
                "total_cases": len(experienced_cases),
                "win_rate": round(exp_win_rate, 1),
                "avg_duration": round(
                sum(c["duration_days"] for c in experienced_cases if c.get("duration_days")) /
                len([c for c in experienced_cases if c.get("duration_days")]) if experienced_cases else 0, 0
                )
                },
                "novice_lawyers": {
                "experience_years": "0-5",
                "total_cases": len(novice_cases),
                "win_rate": round(nov_win_rate, 1),
                "avg_duration": round(
                sum(c["duration_days"] for c in novice_cases if c.get("duration_days")) /
                len([c for c in novice_cases if c.get("duration_days")]) if novice_cases else 0, 0
                )
                },
                "experience_advantage": round(exp_win_rate - nov_win_rate, 1),
                "insights": [
                f"Experienced lawyers have {round(exp_win_rate - nov_win_rate, 1)}% higher win rate",
                "Cases with experienced lawyers resolve faster on average",
                "High-risk cases show better outcomes with experienced representation"
                ]
                }