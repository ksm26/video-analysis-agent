class FinalOutputChecker:
    def __init__(self, output_path):
        self.output_path = output_path

    def validate_output(self):
        """
        Basic validation: adjust based on real output structure.
        """
        with open(self.output_path, 'r') as file:
            content = file.read().lower()
        
        # Example: look for success indicator
        return "test successful" in content or "success" in content
