class HTMLComplexer:
    def __init__(self):
        # Initialize the mapping of keywords to HTML tags and other instance variables
        self.tag_mapping = {
            ".b": "b",
            ".i": "i",
            ".strong": "strong",
            ".e": "em",
            ".u": "u",
            ".sub": "sub",
            ".sup": "sup",
            "d": "del",
            ".ins": "ins",
            ".code": "code",
            ".pre": "pre",
            ".hr": "hr",
            ".m": "marquee",
            ".small": "small",
            ".big": "big",
            ".q": "blockquote",
            ".c": "cite",
            ".kbd": "kbd",
            ".samp": "samp",
            ".var": "var",
            ".address": "address",
            ".details": "details",
            ".summary": "summary",
            ".figcaption": "figcaption",
            ".figure": "figure",
            ".br": "br",
        }
        self.output = []
        self.stack = []

    def process_part(self, part: str):
        if part == "br":
            # Close any open tags and add a <br> tag
            self.close_all_tags()
            self.output.append("<br>")
        elif part == "hr":
            # Close any open tags and add a <hr> tag
            self.close_all_tags()
            self.output.append("<hr>")
        elif part in self.tag_mapping:
            # Handle opening tags
            tag = self.tag_mapping[part]
            self.output.append(f"<{tag}>")
            self.stack.append(tag)
        else:
            # Handle text content
            self.output.append(part)
            self.close_all_tags()
            
    
    def close_all_tags(self):
        # Close all currently open tags
        while self.stack:
            self.output.append(f"</{self.stack.pop()}>")

    def convert_to_html(self, input_text: str) -> str:
        # Split the input text and process each part
        parts = input_text.split()
        for part in parts:
            self.process_part(part)
        # Close any remaining open tags
        self.close_all_tags()
        return ' '.join(self.output)

