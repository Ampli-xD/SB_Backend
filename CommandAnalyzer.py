class CommandProcessor:
    def __init__(self, data):
        self.commands = {
            'storm': self.handle_storm,
            'info': self.handle_info,
            'help': self.handle_help,
            'demo': self.handle_demo,
            'listfiles': self.handle_files,
            'search': self.handle_search,
            'stormAnalyze': self.handle_storm_analyze
        }
        self.room = data['room']
        self.messages = data['messages']
        self.uploaded_data = data['uploaded_data']
        self.online_users = data['online_users']
    
    def handle_storm(self, content):
        # Add more specific logic if needed
        return f"Storm command received with content: {content}"
    
    def handle_info(self, content):
        # Provide room or system information
        return f"Info command received with content: {content}"
    
    def handle_help(self, content):
        # Provide help information
        return "Help command received. Here are some instructions..."
    
    def handle_demo(self, content):
        # Handle demo commands
        return f"Demo command received with content: {content}"
    
    def handle_files(self, content):
        # List or process files in the room
        return f"Files command received with content: {content}"
    
    def handle_search(self, content):
        # Search within the room data (messages, files, etc.)
        return f"Search command received with content: {content}"
    
    def handle_storm_analyze(self, content):
        # Analyze storm-related data or commands
        return f"Storm Analyze command received with content: {content}"
    
    def analyze_command(self, command, content):
        if command in self.commands:
            return self.commands[command](content)
        else:
            return f"Unknown command '{command}'. Type '!help' for a list of commands."
