class ScriptedAgent:
    def __init__(self, lines):
        self.lines = lines
        self.index = 0

    def reply(self, transcript):
        if self.index < len(self.lines):
            line = self.lines[self.index]
        else:
            line = self.lines[-1]
        self.index += 1
        return line