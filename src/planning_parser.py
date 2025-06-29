class PlanningLogParser:
    def __init__(self, log_path):
        self.log_path = log_path

    def parse_steps(self):
        steps = []
        with open(self.log_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    steps.append({
                        "description": line,
                        "action_id": self._generate_action_id(line)
                    })
        return steps

    def _generate_action_id(self, description):
        return description.lower().replace(" ", "_").replace('"', '')
