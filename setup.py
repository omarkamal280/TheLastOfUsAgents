import os
import shutil
import subprocess
import sys

def setup_environment():
    """Set up the environment for the debate orchestrator."""
    print("Setting up environment for The Last of Us Moot Court Debate...")
    
    # Check if .env exists, create from example if not
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("Creating .env file from .env.example...")
            shutil.copy('.env.example', '.env')
            print("Please edit the .env file to add your OpenAI API key.")
        else:
            print("ERROR: .env.example not found!")
            return False
    
    # Check if virtual environment exists
    venv_dir = 'venv'
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
        except subprocess.CalledProcessError:
            print("ERROR: Failed to create virtual environment!")
            return False
    
    # Install requirements
    print("Installing requirements...")
    pip_path = os.path.join(venv_dir, 'Scripts', 'pip') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'pip')
    try:
        subprocess.check_call([pip_path, 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install requirements!")
        return False
    
    print("\nSetup complete!")
    print("\nTo activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print(f"    .\\{venv_dir}\\Scripts\\activate")
    else:  # Unix/Linux
        print(f"    source {venv_dir}/bin/activate")
    
    print("\nTo run the debate orchestrator:")
    print("    python debate_orchestrator.py")
    
    return True

if __name__ == "__main__":
    setup_environment()
