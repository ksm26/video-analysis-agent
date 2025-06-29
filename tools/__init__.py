from src.planning_parser import PlanningLogParser as LogParser


def main():
    
    log_path = "data/planning_logs/run1.txt"

    with open(log_path, "r") as file:
        raw_log = file.read()

    parser = LogParser()
    steps = parser.parse(raw_log)

    print("Parsed Planning Steps:")
    for step in steps:
        print(f"Step {step['step_number']}: {step['description']}")


if __name__ == "__main__":
    main()
