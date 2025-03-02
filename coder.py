import subprocess
import io
import contextlib
import traceback
import sys
import logging
import webbrowser
import os
import re

# Configure logging
logging.basicConfig(filename='generated_code.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_code_with_ollama(user_input):
    # Construct a prompt that instructs the model to generate Python code.
    prompt = f"Write a Python script that {user_input}"
    try:
        # Call the ollama CLI to run the Llama 3.2 model with the prompt.
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2', prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',  # Specify encoding explicitly
            errors='replace',  # Replace any invalid characters
            check=True
        )
        code = result.stdout.strip()
        return code
    except subprocess.CalledProcessError as e:
        return f"Error generating code: {e.stderr}"
    except UnicodeDecodeError as e:
        return f"Error decoding Ollama output: {str(e)}"

def clean_generated_code(code):
    # Remove any non-Python content from the generated code
    cleaned_code = []
    in_code_block = False
    for line in code.split('\n'):
        if line.strip().startswith("```"):
            # Check if this is a Python code block
            if "python" in line.lower() or in_code_block:
                in_code_block = not in_code_block
            continue
        if in_code_block and not any(line.strip().startswith(cmd) for cmd in ["pip", "!", "%", "pip install", "python", "sh", "cmd", "cd"]):
            cleaned_code.append(line)
    
    # If no code was found within code blocks, try to extract all code
    if not cleaned_code:
        for line in code.split('\n'):
            if line.strip() and not any(line.strip().startswith(cmd) for cmd in ["pip", "!", "%", "pip install", "python", "sh", "cmd", "cd"]):
                cleaned_code.append(line)
    
    return '\n'.join(cleaned_code)

def ensure_libraries_in_code_installed(code):
    import re
    required_libraries = re.findall(r'^\s*import\s+(\w+)', code, re.MULTILINE)
    required_libraries += re.findall(r'^\s*from\s+(\w+)', code, re.MULTILINE)
    for lib in set(required_libraries):
        try:
            __import__(lib)
        except ImportError:
            response = input(f"The library '{lib}' is not installed. Do you want to install it? (yes/no): ")
            if response.lower() == 'yes':
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            else:
                print(f"Cannot proceed without installing '{lib}'. Exiting.")
                sys.exit(1)

def run_generated_code(code):
    ensure_libraries_in_code_installed(code)
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        # Create a full environment for execution
        exec_globals = {
            "os": os, 
            "subprocess": subprocess,
            "webbrowser": webbrowser,
            "sys": sys,
            "__name__": "__main__"
        }
        
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exec(code, exec_globals)
    except Exception:
        error_message = f"An error occurred while running the code:\n{traceback.format_exc()}\n{stderr.getvalue()}"
        logging.error(error_message)
        print(error_message)
        return error_message
    output = stdout.getvalue() + stderr.getvalue()
    if not output.strip():
        output = "Code executed successfully, but produced no output."
    logging.info("Execution output:\n" + output)
    print("Execution output:")
    print(output)
    return output

def agent(user_input):
    # Direct handle for browsing requests
    browse_pattern = re.compile(r'browse to (https?://\S+)', re.IGNORECASE)
    browse_match = browse_pattern.search(user_input)
    
    if browse_match:
        url = browse_match.group(1)
        print(f"Opening URL: {url}")
        webbrowser.open(url)
        return f"Opened URL: {url} in your default web browser."
    
    # Step 1: Generate Python code using Ollama:llama3.2
    code = generate_code_with_ollama(user_input)
    print("Generated code:")
    print(code)
    logging.info("Generated code:\n" + code)
    
    # Write the generated code to a file
    with open('generated_code.py', 'w') as f:
        f.write(code)
    
    # Clean the generated code
    code = clean_generated_code(code)
    print("Cleaned code:")
    print(code)
    logging.info("Cleaned code:\n" + code)
    
    # Step 2: Execute the generated code and capture its output
    output = run_generated_code(code)
    return output

# Example usage:
if __name__ == "__main__":
    user_input = "calculates the sum of 2 and 3 and prints the result"
    result = agent(user_input)
    print("Agent output:")
    print(result)
