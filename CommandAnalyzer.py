from HtmlComplexer import HTMLComplexer
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
        self.html_complexer = HTMLComplexer()  # Initialize HTMLComplexer

    def handle_storm(self, content):
        formatted_content = self.html_complexer.convert_to_html(content)
        return f"Storm command received with content: {formatted_content}"
    
    def handle_info(self):
        room_code = self.room.get('code', 'N/A')
        room_name = self.room.get('name', 'N/A')
        creator = self.room.get('creator', 'N/A')
        creation_time = self.room.get('creation_time_utc', 'N/A')
        
        online_users_list = ', '.join(user['name'] for user in self.online_users) if self.online_users else 'No users online'
        
        info_text = (f"<h2>Room Information</h2>",
                    f"<p><b>Name:</b> {room_name}</p>",
                    f"<p><b>Code:</b> {room_code}</p>",
                    f"<p><b>Creator:</b> {creator}</p>",
                    f"<p><b>Creation Time:</b> {creation_time}</p>",
                    f"<p><b>Online Users:</b> {online_users_list}</p>")
        
        formatted_info = self.html_complexer.convert_to_html(info_text)
        return formatted_info
    
    def handle_help(self, content):
        help_text = "Help command received. Here are some instructions..."
        formatted_help = self.html_complexer.convert_to_html(help_text)
        return formatted_help
    
    def handle_demo(self, content):
        formatted_content = self.html_complexer.convert_to_html(content)
        return f"Demo command received with content: {formatted_content}"
    
    def handle_files(self, content):
        formatted_content = self.html_complexer.convert_to_html(content)
        return f"Files command received with content: {formatted_content}"
    
    def handle_search(self, content):
        formatted_content = self.html_complexer.convert_to_html(content)
        return f"Search command received with content: {formatted_content}"
    
    def handle_storm_analyze(self, content):
        formatted_content = self.html_complexer.convert_to_html(content)
        return f"Storm Analyze command received with content: {formatted_content}"
    
    def analyze_command(self, command, content):
        if command in self.commands:
            command_lower = command.lower()
            return self.commands[command_lower](content)
        else:
            unknown_command_text = f"Unknown command '{command}'. Type '!help' for a list of commands."
            formatted_unknown_command = self.html_complexer.convert_to_html(unknown_command_text)
            return formatted_unknown_command
