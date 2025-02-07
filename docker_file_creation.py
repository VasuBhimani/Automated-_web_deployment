from flask import Flask, render_template, request, redirect, url_for, flash
import os
from git import Repo
import requests
import json


def docker_file_creation(username,project_name,extra_text):
    url = 'https://eb3b-136-233-130-145.ngrok-free.app/api/generate'
#----------------------------------------- Reading treefile -------------------------------------------------------------------
    file_path = os.path.abspath(os.path.join('./download/', username, project_name, project_name + '.txt'))
            
    # ✅ Check if the file exists and is readable
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    elif not os.access(file_path, os.R_OK):
        print(f"❌ Permission denied: {file_path}")
        return

    # ✅ Read file content
    try:
        with open(file_path, 'r') as file:
            prompt_content1 = file.read()
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return

    # ✅ Combine prompt with extra text
    full_prompt = "this is file sturcture of my project\n " + prompt_content1 

#--------------------------------------------- Reading dockerfile info ---------------------------------------------------------
    file_path = os.path.abspath(os.path.join('./download/', username, project_name, 'dockerfile_info.txt'))
            
    # ✅ Check if the file exists and is readable
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    elif not os.access(file_path, os.R_OK):
        print(f"❌ Permission denied: {file_path}")
        return

    # ✅ Read file content
    try:
        with open(file_path, 'r') as file:
            prompt_content2 = file.read()
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return

    full_prompt = full_prompt + "\nthis is my project info which may help you to create docker file\n " + prompt_content2 + extra_text
    # print(full_prompt)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"  # ✅ Helps avoid 403 errors
    }

    data = {
        "model": "qwen2.5-coder:32b",
        "prompt": full_prompt,
        "stream": False
    }

    # ✅ Send API request with retry logic
    MAX_RETRIES = 30
    retry_count = 0
    while retry_count < MAX_RETRIES:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            break
        print(f"⚠️ Server returned status code {response.status_code}. Retrying... ({retry_count + 1}/{MAX_RETRIES})")
        time.sleep(2)  # Wait before retrying
        retry_count += 1

    if response.status_code != 200:
        print(f"❌ Failed after {MAX_RETRIES} retries. Exiting.")
        return

    # ✅ Handle API response safely
    try:
        json_res = response.json()
        dockerfile_content = json_res.get("response", "⚠️ No 'response' key found in the JSON.")
        print(dockerfile_content)
    except json.JSONDecodeError:
        print("❌ Error: API returned invalid JSON.")
        print("Raw response:", response.text)

    dockerfile_path = os.path.abspath(os.path.join('./download/', username, project_name, project_name, 'Dockerfile'))

    try:
        with open(dockerfile_path, 'w') as dockerfile:
            dockerfile.write(dockerfile_content)
        print(f"✅ Dockerfile successfully updated at: {dockerfile_path}")
    except Exception as e:
        print(f"❌ Error writing to Dockerfile: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)