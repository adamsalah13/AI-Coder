import sys
import subprocess
import os
import logging
import datetime
from coder import generate_code_with_ollama, clean_generated_code, run_generated_code

# Configure logging
logging.basicConfig(filename='agent.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_libraries_installed():
    required_libraries = ["subprocess", "io", "contextlib", "traceback"]
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            response = input(f"The library '{lib}' is not installed. Do you want to install it? (yes/no): ")
            if response.lower() == 'yes':
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            else:
                print(f"Cannot proceed without installing '{lib}'. Exiting.")
                sys.exit(1)

class AgenticTool:
    def __init__(self, user_input):
        self.user_input = user_input
        self.generated_code = ""
        self.output = ""
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

    def generate_code(self):
        print(f"Generating code for task: {self.user_input}")
        logging.info(f"Generating code for task: {self.user_input}")
        
        # Make the prompt more specific to only do exactly what was asked
        if "browse to" in self.user_input.lower():
            url = self.user_input.lower().split("browse to")[1].strip()
            task_prompt = f"""
Write a simple Python script that opens the URL {url} in a web browser.
Use webbrowser.open() and nothing else. Don't run any terminal commands.
Just open the browser to that specific URL and print a success message.
"""
        else:
            task_prompt = f"""
Write a Python script that {self.user_input}. 
Include all necessary imports.
If you need to open a browser, use webbrowser.open().
If you need to run terminal commands on Windows, use subprocess.run('command', shell=True).
Do not include any additional unnecessary actions.
Make sure the script is complete and can be executed directly.
"""
        raw_code = generate_code_with_ollama(task_prompt)
        
        # Log the raw generated code
        logging.info(f"Raw generated code:\n{raw_code}")
        with open(f'logs/raw_code_{self.timestamp}.py', 'w') as f:
            f.write(raw_code)
            
        # Clean the code
        self.generated_code = clean_generated_code(raw_code)
        
        # Log the cleaned code
        logging.info(f"Cleaned code:\n{self.generated_code}")
        with open(f'logs/cleaned_code_{self.timestamp}.py', 'w') as f:
            f.write(self.generated_code)
        
        # Also save the current code
        with open('generated_code.py', 'w') as f:
            f.write(self.generated_code)

    def run_code(self):
        logging.info("Executing generated code")
        self.output = run_generated_code(self.generated_code)
        logging.info(f"Execution result: {self.output}")
        return self.output

    def execute(self):
        self.generate_code()
        return self.run_code()

# Example usage:
if __name__ == "__main__":
    ensure_libraries_installed()
    
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        user_input = input("Enter the task description: ")
    
    tool = AgenticTool(user_input)
    result = tool.execute()
    print("Agentic Tool output:")
    print(result)
