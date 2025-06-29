import os
import datetime

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, run_name, results, output_file_path=None, video_path=None, token_usage=None, duration_sec=None, logs=None, html=False):
        """
        Generates both .txt and optional .html reports with technical details.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_report_path = os.path.join(self.output_dir, f"{run_name}_detailed_report_{timestamp}.txt")

        # Shared content builder
        report_content = []
        report_content.append(f"Test Suite: {run_name}")
        report_content.append("=" * 50)
        report_content.append(f"Total Duration: {duration_sec:.2f} sec")
        report_content.append(f"Total Token Used: {token_usage.get('total_tokens', 0) if token_usage else 'N/A'}")
        report_content.append(f"Total Cost Estimate: {token_usage.get('total_cost', 'N/A')} USD\n")

        report_content.append("Test Result Summary")
        report_content.append("-" * 50)
        passed_steps = sum(1 for res in results if res['result'] == "✅ Observed")
        failed_steps = len(results) - passed_steps
        report_content.append(f"Steps Passed: {passed_steps}")
        report_content.append(f"Steps Failed: {failed_steps}\n")

        report_content.append("Detailed Steps:")
        report_content.append("-" * 50)
        for idx, res in enumerate(results, 1):
            report_content.append(f"Step {idx}: {res['description']}")
            report_content.append(f"  Result: {res['result']}")
            report_content.append(f"  Notes: {res['notes']}\n")

        if output_file_path:
            report_content.append(f"Output File: {output_file_path}")
        if video_path:
            report_content.append(f"Proofs Video: {video_path}")
        if logs:
            report_content.append(f"Planner Thoughts Log: {logs.get('thoughts', 'N/A')}")
            report_content.append(f"Chat Messages Log: {logs.get('chat', 'N/A')}")

        # Generate .txt report
        with open(txt_report_path, "w") as report_file:
            report_file.write("\n".join(report_content))
        
        print(f"[INFO] Text report generated: {txt_report_path}")

        # Optional HTML report
        if html:
            html_report_path = os.path.join(self.output_dir, f"{run_name}_detailed_report_{timestamp}.html")
            self._generate_html_report(html_report_path, report_content)
            print(f"[INFO] HTML report generated: {html_report_path}")

    def _generate_html_report(self, path, lines):
        """
        Basic HTML formatting for report content.
        """
        with open(path, "w") as html_file:
            html_file.write("<html><head><title>Test Report</title></head><body>")
            html_file.write("<h2>Test Report Details</h2><pre>")
            for line in lines:
                html_file.write(f"{line}\n")
            html_file.write("</pre></body></html>")
