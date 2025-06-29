import os
import time
import datetime
from langchain.llms import HuggingFacePipeline
from langchain.agents import initialize_agent, AgentType
from transformers import pipeline, AutoTokenizer
from src.input_handler import InputHandler
from src.planning_parser import PlanningLogParser
from src.video_analyzer import VideoAnalyzer
from src.output_checker import FinalOutputChecker
from src.deviation_engine import DeviationEngine
from src.report_generator import ReportGenerator

# === Model Setup ===
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

hf_pipeline = pipeline("text-generation", model=MODEL_NAME, max_new_tokens=300)
llm = HuggingFacePipeline(pipeline=hf_pipeline)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# === Directories ===
VIDEO_DIR = "data/videos"
LOG_DIR = "data/planning_logs"
OUTPUT_DIR = "data/test_outputs"
REPORT_DIR = "reports"
LOG_FILE_DIR = "./log_files"

os.makedirs(LOG_FILE_DIR, exist_ok=True)

# === Initialize ===
input_handler = InputHandler(VIDEO_DIR, LOG_DIR, OUTPUT_DIR)
reporter = ReportGenerator(REPORT_DIR)
from tools.ai_tools import parse_planning_log, analyze_video_for_action, validate_final_output

tools = [parse_planning_log, analyze_video_for_action, validate_final_output]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True
)

# prompt_template = (
#     "You are an AI test validation agent.\n"
#     "You have access to these tools:\n"
#     "- parse_planning_log\n"
#     "- analyze_video_for_action\n"
#     "- validate_final_output\n"
#     "\nYour response must follow this strict structure:\n"
#     "Thought: Your reasoning here\n"
#     "Action: tool_name_here\n"
#     "Action Input: your_tool_arguments_here\n"
#     "\nExample:\n"
#     "Thought: I need to parse the log first.\n"
#     "Action: parse_planning_log\n"
#     "Action Input: log_path=data/planning_logs/run1.txt\n"
#     "\nNow process the following:\n"
#     "Planning Log:\n"
#     "{planning_log}\n"
# )


# === Main Loop ===
for log_path in input_handler.get_planning_logs():
    run_name = os.path.splitext(os.path.basename(log_path))[0]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"[INFO] Starting analysis for: {run_name}")

    videos = input_handler.get_videos()
    output_files = input_handler.get_final_outputs()

    if not videos or not output_files:
        print(f"[WARN] Missing videos or output for {run_name}. Skipping.")
        continue

    with open(log_path, "r") as file:
        planning_log = file.read()

    final_prompt = (
        f"You are an AI validation agent.\n"
        f"Your task is to extract intended steps from the following planning log.\n"
        f"Use the available tools to complete the task.\n"
        f"Planning Log:\n{planning_log}\n"
        f"The log file is located at {log_path}."
    )

    start_time = time.time()

    response_text = agent.run(final_prompt).strip()

    prompt_tokens = tokenizer(final_prompt, return_tensors="pt").input_ids.shape[1]
    response_tokens = tokenizer(response_text, return_tensors="pt").input_ids.shape[1]

    total_tokens = prompt_tokens + response_tokens
    total_cost = (total_tokens / 1000) * 0.002

    thoughts_path = os.path.join(LOG_FILE_DIR, f"{run_name}_planner_thoughts_{timestamp}.log")
    chat_path = os.path.join(LOG_FILE_DIR, f"{run_name}_chat_messages_{timestamp}.log")

    with open(thoughts_path, "w") as f:
        f.write(f"Prompt Sent:\n{final_prompt}\n")
        f.write(f"AI Thought Process:\n{response_text}\n")

    with open(chat_path, "w") as f:
        f.write(f"Prompt:\n{final_prompt}\n")
        f.write(f"Response:\n{response_text}\n")

    # === Step Validation with Tools ===
    parser = PlanningLogParser(log_path)
    steps = parser.parse_steps()

    deviation_engine = DeviationEngine()

    for step in steps:
        action_id = step["action_id"]
        description = step["description"]

        analyzer = VideoAnalyzer(videos[0])
        found, timestamp_sec = analyzer.analyze_for_action(action_id)

        deviation_engine.record_step(description, found, timestamp_sec)

    results = deviation_engine.get_results()
    output_checker = FinalOutputChecker(output_files[0])
    output_valid = output_checker.validate_output()

    duration_sec = time.time() - start_time

    logs = {
        "thoughts": thoughts_path,
        "chat": chat_path
    }

    token_usage = {
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 5)
    }

    reporter.generate_report(
        run_name=run_name,
        results=results,
        output_file_path=output_files[0],
        video_path=videos[0],
        token_usage=token_usage,
        duration_sec=duration_sec,
        logs=logs,
        html=True
    )

    if output_valid:
        print(f"[INFO] Final output for {run_name} is consistent.")
    else:
        print(f"[WARN] Final output for {run_name} shows inconsistencies.")
