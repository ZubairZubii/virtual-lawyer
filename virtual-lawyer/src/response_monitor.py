# src/response_monitor.py

import datetime

class ResponseMonitor:
    def __init__(self):
        self.logs = []

    def log_response(self, user_input, bot_response, response_time, quality_score):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "response_time": response_time,
            "quality_score": quality_score
        }
        self.logs.append(log_entry)
        print(f"[🧠 LOGGED] {user_input[:50]}... | Score: {quality_score}")

    def get_recent_logs(self, n=10):
        return self.logs[-n:]
