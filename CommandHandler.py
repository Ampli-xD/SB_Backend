import CommandAnalyzer as CA
class commandHandler:
    def __init__(self, message, data):
        self.content = message['content']
        self.CommandAnalyzer= CA.CommandProcessor(data)
    def commandSplitter(self, command_text):
        parts = command_text[1:].split(maxsplit=1)
        command = parts[0]
        content = parts[1]
        return ('!', command, content)
    def analyzeCommand(self):
        splitted = self.commandSplitter(self.content)
        return self.CommandAnalyzer.analyze_command(splitted[1], splitted[2]) , splitted[1]