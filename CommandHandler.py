import re

def extract_commands(message):
	# Use regex to find all occurrences of @ followed by a word
	matches = re.findall(r'@(\w+)', message)
	return matches

# Example usage
message = "Hello @storm, please meet @john and @doe."
commands = extract_commands(message)
print(commands)  # Output: ['storm', 'john', 'doe']
