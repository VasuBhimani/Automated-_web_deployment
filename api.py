import os
import requests
import json

def docker_file_creation(file_name, extra_text):
    file_path = os.path.join('./download/', 'vasu', 'AWS_SCD_booth', file_name)
    url = 'https://eb3b-136-233-130-145.ngrok-free.app/api/generate'
    # url= 'https://myhostd23it165.loca.lt/api/generate'

    try:
        with open(file_path, 'r') as file:
            prompt_content = file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return

    full_prompt = prompt_content + extra_text

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen2.5-coder:32b",
        # "model": "deepseek-r1:32b",
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        # Retry logic if the response code is not 200
        while response.status_code != 200:
            print(f"Server returned status code {response.status_code}. Retrying...")
            response = requests.post(url, headers=headers, json=data)

        # Parse the response as JSON
        json_res = response.json()  # Use `response.json()` for JSON parsing directly
        
        # Extract and print only the 'response' field
        dockerfile_content = json_res.get("response", "No 'response' key found in the JSON response")
        print(dockerfile_content)

    except json.JSONDecodeError:
        print("Error: Response is not a valid JSON.")
        print("Raw response text:", response.text)
    except requests.RequestException as e:
        print(f"Error during the request: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


file_name = 'AWS_SCD_booth_structure.txt'
extra_text = "create production ready docker file for this file structure and just create docker file with following Best Practices dont give me other explanation or comments and without markdown"

docker_file_creation(file_name, extra_text)
