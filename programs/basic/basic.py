import json
import os
import requests

def queue_workflow(workflow):
    # ComfyUI server endpoint
    url = "http://127.0.0.1:8188/prompt"
    
    # Send POST request to queue the prompt
    response = requests.post(url, json={"prompt": workflow})
    
    if response.status_code == 200:
        print("Prompt queued successfully")
    else:
        print(f"Error queuing prompt: {response.status_code}")
        print(response.text)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
workflow_path = os.path.join(script_dir, 'workflow.json')

# Load the prompt template from JSON file
with open(workflow_path, 'r') as f:
    workflow = json.load(f)

# Ask the user for the prompt. If the user doesn't enter anything, use the default prompt.
user_prompt = input("Enter what you want to draw (e.g., 'a beautiful sunset over mountains'): ")
if user_prompt:
    workflow["6"]["inputs"]["text"] = user_prompt

# Queue the prompt
queue_workflow(workflow)

