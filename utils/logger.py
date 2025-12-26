def get_logger(name=None):
    class Logger:
        def info(self, msg): print(msg)
        def error(self, msg): print(msg)
        def warning(self, msg): print(msg)
    return Logger()
