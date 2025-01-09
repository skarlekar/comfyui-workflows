import json
import os
import requests
import uuid

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
    
    return response.status_code

def process_workflow(workflow_path, user_prompt, negative_prompt, seed):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workflow_path = os.path.join(script_dir, workflow_path)

    # Load the prompt template from JSON file
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)

    # Update the workflow with user prompt if provided
    if user_prompt:
        workflow["4"]["inputs"]["text"] = user_prompt
        
    # Update the negative prompt if provided
    if negative_prompt:
        workflow["6"]["inputs"]["text"] = negative_prompt
        
    # Update the seed value if provided
    if seed is not None:
        workflow["3"]["inputs"]["seed"] = seed
        
    return workflow

def main():
    # Ask the user for the positive prompt
    user_prompt = input("Enter what you want to draw (e.g., 'a beautiful sunset over mountains'): ")
    
    # Ask the user for the negative prompt
    negative_prompt = input("Enter what you do not want to see (e.g., extra limbs, bad eyes, bad anatomy, cropped, cross-eyed, worst quality, low quality): ")
    
    # Ask the user for the seed value
    seed_input = input("Enter a seed value (press Enter for random): ")
    seed = int(seed_input) if seed_input.strip() else None
    
    workflow = process_workflow('workflow2.json', user_prompt, negative_prompt, seed)
    queue_workflow(workflow)

if __name__ == "__main__":
    main()

