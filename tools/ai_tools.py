from langchain.tools import tool
from src.planning_parser import PlanningLogParser
from src.video_analyzer import VideoAnalyzer
from src.output_checker import FinalOutputChecker

@tool
def parse_planning_log(log_path: str):
    """
    Parse planning log file to extract intended steps.
    """
    parser = PlanningLogParser(log_path)
    steps = parser.parse_steps()
    return steps

@tool
def analyze_video_for_action(input_text: str):
    """
    Analyzes video to detect presence of an action.
    Expects input_text in format: 'video_path=<path>; action_id=<id>'
    """
    try:
        parts = dict(item.strip().split("=") for item in input_text.split(";"))
        video_path = parts.get("video_path")
        action_id = parts.get("action_id")
        
        analyzer = VideoAnalyzer(video_path)
        found, timestamp = analyzer.analyze_for_action(action_id)
        return {"found": found, "timestamp": timestamp}
    
    except Exception as e:
        return {"error": str(e)}

@tool
def validate_final_output(output_path: str):
    """
    Validate final test output for consistency.
    """
    checker = FinalOutputChecker(output_path)
    success = checker.validate_output()
    return success
