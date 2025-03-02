import os
import subprocess
import sys
import venv
import platform

def create_virtual_environment():
    """Create a Python virtual environment"""
    print("Creating virtual environment...")
    venv_dir = os.path.join(os.getcwd(), "coder_env")
    venv.create(venv_dir, with_pip=True)
    return venv_dir

def is_venv_activated():
    """Check if a virtual environment is activated"""
    return (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def get_python_executable(venv_dir):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")

def install_dependencies(python_executable):
    """Install required dependencies"""
    print("Installing dependencies...")
    packages = [
        "requests",
        "beautifulsoup4",
        "matplotlib",
        "numpy",
        "pillow",
    ]
    
    subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([python_executable, "-m", "pip", "install"] + packages)

def create_directories():
    """Create required directories"""
    print("Creating project directories...")
    directories = ["logs", "docs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return True
        return False
    except FileNotFoundError:
        return False

def main():
    print("Setting up Coding Agent environment...")
    
    # Check if we're in a virtual environment already
    if not is_venv_activated():
        venv_dir = create_virtual_environment()
        python_executable = get_python_executable(venv_dir)
        print(f"Virtual environment created at: {venv_dir}")
        print(f"Activate it with: ")
        if platform.system() == "Windows":
            print(f"    {os.path.join(venv_dir, 'Scripts', 'activate')}")
        else:
            print(f"    source {os.path.join(venv_dir, 'bin', 'activate')}")
    else:
        python_executable = sys.executable
        print("Using existing virtual environment.")
    
    install_dependencies(python_executable)
    create_directories()
    
    # Check Ollama installation
    if not check_ollama_installed():
        print("\nWARNING: Ollama doesn't appear to be installed or is not in the PATH.")
        print("Please install Ollama from https://ollama.ai/")
        print("After installing Ollama, run: ollama pull llama3.2")
    else:
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True
            )
            if "llama3.2" not in result.stdout:
                print("\nPulling Llama 3.2 model...")
                subprocess.run(["ollama", "pull", "llama3.2"])
            else:
                print("\nLlama 3.2 model is already installed.")
        except Exception as e:
            print(f"Error checking Llama model: {e}")
    
    print("\nSetup complete! Your coding agent environment is ready.")
    print("Run the agent with: python agentic_tool.py")

if __name__ == "__main__":
    main()
