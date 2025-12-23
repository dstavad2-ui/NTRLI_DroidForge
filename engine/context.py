import os
import json

class ExecutionContext:
    def __init__(self, event, env):
        self.event = event
        self.env = env
        self.commands = []

def build_context():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event = {}

    if event_path and os.path.exists(event_path):
        with open(event_path, "r", encoding="utf-8") as f:
            event = json.load(f)

    return ExecutionContext(event=event, env=dict(os.environ))
