from langchain.tools import tool
from src.planning_parser import PlanningLogParser
from src.video_analyzer import VideoAnalyzer
from src.output_checker import FinalOutputChecker

@tool
def parse_planning_log(input_text: str):
    """
    Parses planning log at runtime.
    Expects: 'log_path=<path>'
    """
    try:
        path = input_text.strip().split("=")[-1]
        parser = PlanningLogParser(path)
        steps = parser.parse_steps()
        return steps
    except Exception as e:
        return {"error": str(e)}

@tool
def analyze_video_for_action(input_text: str):
    """
    Analyzes video to detect presence of an action.
    Expects: 'video_path=<path>; action_id=<id>'
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
def validate_final_output(input_text: str):
    """
    Validate final output at runtime.
    Expects: 'output_path=<path>'
    """
    try:
        path = input_text.strip().split("=")[-1]
        checker = FinalOutputChecker(path)
        success = checker.validate_output()
        return success
    except Exception as e:
        return {"error": str(e)}
