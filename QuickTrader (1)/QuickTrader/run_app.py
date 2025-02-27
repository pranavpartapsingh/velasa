import os
import subprocess
import sys

if __name__ == "__main__":
    # Set the server port
    os.environ['STREAMLIT_SERVER_PORT'] = '5000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

    # Run the app using subprocess
    try:
        subprocess.run(["streamlit", "run", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit not found. Please make sure you have installed all requirements.")
        print("Run: pip install streamlit==1.42.2")
        sys.exit(1)