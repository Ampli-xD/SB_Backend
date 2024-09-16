from HtmlComplexer import HTMLComplexer
class CommandProcessor:
    def __init__(self, data, instance_tuple):
        self.commands = {
            'storm': self.handle_storm,
            'info': self.handle_info,
            'help': self.handle_help,
            'demo': self.handle_demo,
            'listfiles': self.handle_files,
            'search': self.handle_search,
            'stormAnalyze': self.handle_storm_analyze
        }
        self.gemini_instance = instance_tuple[0]
        self.pinecone_instance = instance_tuple[1]
        self.room = data['room']
        self.messages = data['messages']
        self.uploaded_data = data['uploaded_data']
        self.online_users = data['online_users']
        self.html_complexer = HTMLComplexer()  # Initialize HTMLComplexer

    def handle_storm(self, content):
        gemini = self.gemini_instance
        response = gemini.chat(content)
        formatted_content = self.html_complexer.convert_to_html(response)
        return formatted_content
    
    def handle_info(self, content):
        room_code = self.room.get('code', 'N/A')
        room_name = self.room.get('name', 'N/A')
        creator = self.room.get('creator', 'N/A')
        creation_time = self.room.get('creation_time_utc', 'N/A')
        
        print(self.online_users)
        online_users_list = ', '.join(user['name'] for user in self.online_users['users']) if self.online_users else 'No users online'
        
        info_text = (f'''.b Room Information .br
                    .b Name: .cl {room_name} .br
                    .b Code: .cl {room_code} .br
                    .b Creator: .cl {creator} .br
                    .b Creation Time: .cl {creation_time} .br
                    .b Online Users: .cl {online_users_list} .br''')
        
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
        vectordb = self.pinecone_instance
        results = vectordb.query_vectordb(content)
        formatted_content = """<table><thead>
        <tr><th>Score</th><th>Content</th><th>ID</th><th>Filename</th></tr>
        """
        for score, id, filename, chunk in results:
            formatted_content+=f"""<tr><td>{score}</td><td>{chunk}</td><td>{id}</td><td>{filename}</td></tr>"""
        formatted_content+="""</thead></table>"""
        return formatted_content
    
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
