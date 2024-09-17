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
            ".d": "del",
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
            ".ul": "ul",
            ".li": "li",
            ".table": "table",
            ".tr": "tr",
            ".td": "td"
        }
        self.output = []
        self.stack = []

    def process_part(self, part: str):
        if part == ".br":
            # Close any open tags and add a <br> tag
            self.close_all_tags()
            self.output.append("<br>")
        elif part == ".hr":
            # Close any open tags and add a <hr> tag
            self.close_all_tags()
            self.output.append("<hr>")
        elif part == ".cl":
            self.close_all_tags()
        elif part in self.tag_mapping:
            tag = self.tag_mapping[part]
            if tag == "li":
                # Handle list item within a list
                if self.stack and self.stack[-1] == "ul":
                    self.close_all_tags()  # Close any open list item tags
                self.output.append(f"<{tag}>")
                self.stack.append(tag)
            elif tag in ["tr", "td"]:
                # Handle table row and table data
                if tag == "tr":
                    if self.stack and self.stack[-1] == "td":
                        self.close_all_tags()  # Close any open table data tags
                    if self.stack and self.stack[-1] == "table":
                        self.output.append(f"<{tag}>")
                        self.stack.append(tag)
                else:  # for "td"
                    if self.stack and self.stack[-1] == "tr":
                        self.output.append(f"<{tag}>")
                        self.stack.append(tag)
            elif tag == "table":
                # Handle table opening
                self.close_all_tags()
                self.output.append(f"<{tag}>")
                self.stack.append(tag)
            else:
                # Handle other tags
                self.close_all_tags()
                self.output.append(f"<{tag}>")
                self.stack.append(tag)
        else:
            # Handle text content
            self.output.append(part)
    
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
