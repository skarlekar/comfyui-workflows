import json
import os
import streamlit as st
import pandas as pd
import requests
import random
import uuid
import time
import glob

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

def load_styles():
    # Read the CSV file
    df = pd.read_csv('styles.csv')
    
    # Create a dictionary of styles and their substyles
    styles_dict = {}
    current_style = None
    
    for _, row in df.iterrows():
        name = row['name']
        if name.startswith('|||'):
            # This is a main style
            current_style = name.replace('|||', '').strip()
            styles_dict[current_style] = []
        elif '|' in name:
            # This is a substyle
            styles_dict[current_style].append({
                'name': name.split('|')[1].strip(),
                'prompt': row['prompt'],
                'negative_prompt': row['negative_prompt']
            })
    
    return styles_dict

def wait_for_image(unique_id, timeout=60):
    """Wait for image file with the given prefix to appear in the downloads folder."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Look for files with the unique_id prefix
        pattern = os.path.join(r"C:\Users\skarl\Downloads\temp", f"{unique_id}*.png")
        files = glob.glob(pattern)
        if files:
            return files[0]  # Return the first matching file
        time.sleep(1)  # Wait 1 second before checking again
    return None

def main():
    # Initialize session state
    if 'generate_clicked' not in st.session_state:
        st.session_state.generate_clicked = False
    if 'unique_id' not in st.session_state:
        st.session_state.unique_id = None

    def on_generate_click():
        st.session_state.generate_clicked = True
        st.session_state.combined_positive = combined_positive
        st.session_state.combined_negative = combined_negative
        st.session_state.seed = seed
        st.session_state.unique_id = "output_" + str(uuid.uuid4())[:8]

    st.title("Mixed Style Image Generator")
    
    # Add text areas for positive and negative prompts at the top
    user_prompt = st.text_area(
        "Enter what you want to draw",
        placeholder="e.g., a beautiful sunset over mountains",
        height=100
    )
    
    negative_prompt = st.text_area(
        "Enter what you do not want to see",
        placeholder="e.g., extra limbs, bad eyes, bad anatomy, cropped, cross-eyed, worst quality, low quality",
        height=100
    )
    
    # Add seed input with random default value
    default_seed = random.randint(1, 1000000)
    seed = st.number_input("Enter seed value (or keep random)", value=default_seed)
    
    # Load styles
    styles_dict = load_styles()
    
    # Create multiselect for main styles
    selected_styles = st.multiselect(
        "Select Styles",
        options=list(styles_dict.keys())
    )
    
    # Dictionary to store selected substyles for each style
    selected_substyles = {}
    
    # Create multiselect for substyles for each selected style
    for style in selected_styles:
        substyle_options = [sub['name'] for sub in styles_dict[style]]
        selected_substyles[style] = st.multiselect(
            f"Select substyles for {style}",
            options=substyle_options
        )
    
    if st.button("Generate Prompts"):
        positive_prompts = []
        negative_prompts = []
        
        # Add user prompts first if they exist
        if user_prompt:
            positive_prompts.append(user_prompt)
        if negative_prompt:
            negative_prompts.append(negative_prompt)
        
        # Collect prompts for all selected substyles
        for style in selected_styles:
            for substyle_name in selected_substyles[style]:
                # Find the substyle data
                substyle_data = next(
                    sub for sub in styles_dict[style] 
                    if sub['name'] == substyle_name
                )
                
                if substyle_data['prompt']:
                    positive_prompts.append(substyle_data['prompt'])
                if substyle_data['negative_prompt']:
                    negative_prompts.append(substyle_data['negative_prompt'])
        
        # Combine prompts
        combined_positive = ", ".join(positive_prompts)
        combined_negative = ", ".join(negative_prompts)
        
        # Display results
        st.text_area("Positive Prompt", combined_positive, height=150)
        st.text_area("Negative Prompt", combined_negative, height=150)
        
        # Add Generate Image button if prompts are not empty
        if combined_positive:
            st.button("Generate Image", key="generate_image", on_click=on_generate_click)

    # Handle image generation in a separate block
    if st.session_state.generate_clicked:
        try:
            print("Processing workflow...")
            st.write("Processing workflow...")
            workflow = process_workflow('workflow2.json', 
                                     st.session_state.combined_positive, 
                                     st.session_state.combined_negative, 
                                     st.session_state.seed)
            
            # Use the stored unique ID
            workflow["9"]["inputs"]["filename_prefix"] = st.session_state.unique_id
            
            st.write("Queueing workflow...")
            status_code = queue_workflow(workflow)
            
            if status_code == 200:
                st.success("Image generation started successfully!")
                
                # Wait for the image file
                st.write("Waiting for image generation to complete...")
                image_path = wait_for_image(st.session_state.unique_id)
                
                if image_path:
                    st.write("Image generated successfully!")
                    # Display the image
                    st.image(image_path, caption="Generated Image")
                else:
                    st.error("Timeout waiting for image generation")
            else:
                st.error(f"Failed to queue image generation. Status code: {status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")
            st.error(f"Error generating image: {str(e)}")
        finally:
            st.session_state.generate_clicked = False

if __name__ == "__main__":
    main() 