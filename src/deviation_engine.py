class DeviationEngine:
    def __init__(self):
        self.results = []

    def record_step(self, description, observed, timestamp=None):
        result = {
            "description": description,
            "result": "✅ Observed" if observed else "❌ Deviation",
            "notes": f"At {timestamp}s" if observed and timestamp else "Action not found in video"
        }
        self.results.append(result)

    def get_results(self):
        return self.results
