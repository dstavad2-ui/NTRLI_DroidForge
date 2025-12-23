class StateManager:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.data = {}

    def load(self):
        return self.data if self.enabled else {}

    def persist(self, key, value):
        if self.enabled:
            self.data[key] = value
