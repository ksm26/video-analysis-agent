class BaseAgent:
    def __init__(self, tools=None):
        self.tools = tools or []

    def run_step(self, step_description):
        """Orchestrate tool usage based on step"""
        # Placeholder: Extend with LLM reasoning 
        raise NotImplementedError
