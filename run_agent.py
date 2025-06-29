import os
from transformers import pipeline, AutoTokenizer
from src.input_handler import InputHandler
from src.planning_parser import PlanningLogParser # Tool: Parses planning steps
from src.video_analyzer import VideoAnalyzer # Tool: Video analysis for actions
from src.output_checker import FinalOutputChecker # Tool: Final output validation
from src.deviation_engine import DeviationEngine
from src.report_generator import ReportGenerator
import time, datetime
from config.settings import VIDEO_DIR, LOG_DIR, OUTPUT_DIR, REPORT_DIR, LLM_MODEL, COST_PER_1000_TOKENS

# Setup lightweight text generation pipeline
generator = pipeline("text2text-generation", model=LLM_MODEL)
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)

input_handler = InputHandler(VIDEO_DIR, LOG_DIR, OUTPUT_DIR)
reporter = ReportGenerator(REPORT_DIR)

# Initialize counters
total_tokens = 0

# Processing Loop
for log_path in input_handler.get_planning_logs():
    run_name = os.path.splitext(os.path.basename(log_path))[0]
    print(f"\n[INFO] Starting analysis for: {run_name}")

    videos = input_handler.get_videos()
    output_files = input_handler.get_final_outputs()

    if not videos or not output_files:
        print(f"[WARN] Missing videos or output for {run_name}. Skipping.")
        continue

    log_dir = "./log_files"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    thoughts_path = os.path.join(log_dir, f"{run_name}_planner_thoughts_{timestamp}.log")
    chat_path = os.path.join(log_dir, f"{run_name}_chat_messages_{timestamp}.log")

    # Actual prompt construction
    with open(log_path, "r") as file:
        planning_log = file.read()

    prompt = (
    "You are an AI test validation agent.\n"
    "Your task:\n"
    "- Read the planning log below\n"
    "- Think step by step to extract the intended actions\n"
    "- Clearly state your reasoning as 'Thought:' before listing steps\n"
    "\nPlanning Log:\n"
    f"{planning_log}\n"
    "\nRespond with:\nThought: <reasoning>\nSteps: <step list>"
    )
    
    # Token count for prompt
    prompt_tokens = tokenizer(prompt, return_tensors="pt").input_ids.shape[1]
    total_tokens += prompt_tokens
    
    response = generator(prompt, max_new_tokens=200)
    response_text = response[0]["generated_text"]

    thought = "N/A"
    steps_text = response_text

    if "Thought:" in response_text and "Steps:" in response_text:
        parts = response_text.split("Steps:")
        thought_section = parts[0].split("Thought:")[-1].strip()
        steps_section = parts[1].strip()
        thought = thought_section
        steps_text = steps_section

    # Log actual prompt and response
    with open(thoughts_path, "w") as f:
        f.write("=== Planner Thoughts Log ===\n")
        f.write(f"Prompt Sent:\n{prompt}\n\n")
        f.write(f"AI Thought Process:\n{thought}\n")

    with open(chat_path, "w") as f:
        f.write("=== Chat Messages Log ===\n")
        f.write(f"System: Please extract steps with reasoning.\n")
        f.write(f"User Prompt:\n{prompt}\n")
        f.write(f"LLM Full Response:\n{response_text}\n")

    # Token count for response
    response_tokens = tokenizer(response_text, return_tensors="pt").input_ids.shape[1]
    total_tokens += response_tokens

    # print(f"[INFO] LLM Extracted Steps:\n{response}\n")
    print(f"[INFO] LLM Extracted Steps:\n{response_text}\n")
    print(f"[INFO] Tokens used - Prompt: {prompt_tokens}, Response: {response_tokens}")

    # Fallback to deterministic parser
    parser = PlanningLogParser(log_path)
    start_time = time.time()
    steps = parser.parse_steps()

    deviation_engine = DeviationEngine()

    for step in steps:
        action_id = step["action_id"]
        description = step["description"]

        # TOOL USAGE: VideoAnalyzer (detect action in video)
        analyzer = VideoAnalyzer(videos[0])
        found, timestamp = analyzer.analyze_for_action(action_id)

        deviation_engine.record_step(description, found, timestamp)

    results = deviation_engine.get_results()

    # TOOL USAGE: FinalOutputChecker (validate test output)
    output_checker = FinalOutputChecker(output_files[0])
    output_valid = output_checker.validate_output()
    end_time = time.time()
    duration_sec = end_time - start_time

    # Simulated cost estimate (local LLM, no real charges)
    total_cost = (total_tokens / 1000) * COST_PER_1000_TOKENS

    token_usage = {
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 5)
    }

    logs = {
        "thoughts": thoughts_path,
        "chat": chat_path
    }

    reporter.generate_report(
        run_name=run_name,
        results=results,
        output_file_path=output_files[0],
        video_path=videos[0],
        token_usage=token_usage,
        duration_sec=duration_sec,
        logs=logs,
        html=True  # Generates both .txt and .html reports
    )

    if output_valid:
        print(f"[INFO] Final output for {run_name} is consistent.")
    else:
        print(f"[WARN] Final output for {run_name} shows inconsistencies.")

    # Reset token counter for next test run (optional)
    total_tokens = 0
