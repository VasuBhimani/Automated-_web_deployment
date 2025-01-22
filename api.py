import os
import requests
def docker_file_creation(file_name, extra_text):
    file_path = os.path.join('./download/', 'vasu' , 'AWS_SCD_booth', file_name)
    url = 'https://myhost.loca.lt/api/generate'

    with open(file_path, 'r') as file:
        prompt_content = file.read()

    with open(file_path, 'r') as file:
        prompt_content = file.read()

    full_prompt = prompt_content + extra_text

    headers = {
    }

    data = { 
        "model": "qwen2.5-coder:32b",
        "prompt":full_prompt,
        "stream":False
        }

    response = requests.post(url, headers=headers, json=data)
    while response.status_code != 200:
       response = requests.post(url, headers=headers, json=data)
    #    time.sleep(1000)
       print(response.status_code)

    global json_res
    try:
        json_res = json.loads(response.text)
        print(json_res["response"])
    except:
        print("Error parsing JSON")


file_name = 'AWS_SCD_booth_structure.txt' 
extra_text = "create production ready docker file for this file structure and just create docker file dont give me other explaination or comments and without markdown"

docker_file_creation(file_name, extra_text)
