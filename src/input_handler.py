import os

class InputHandler:
    def __init__(self, video_dir, log_dir, output_dir):
        self.video_dir = video_dir
        self.log_dir = log_dir
        self.output_dir = output_dir

    def get_videos(self):
        return [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir) if f.endswith(('.mp4', '.avi'))]

    def get_planning_logs(self):
        return [os.path.join(self.log_dir, f) for f in os.listdir(self.log_dir) if f.endswith(('.txt', '.json'))]

    def get_final_outputs(self):
        return [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith(('.txt', '.json'))]
