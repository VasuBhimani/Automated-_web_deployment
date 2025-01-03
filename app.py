from flask import Flask, render_template, request, redirect, url_for, flash
import os
from git import Repo
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random key

# Ensure the download directory exists
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def generate_tree(root_path, level=0):
    """Generates a tree structure (indented) of the given directory, excluding the .git folder."""
    tree_str = ""
    items = sorted(os.listdir(root_path))
    for item in items:
        item_path = os.path.join(root_path, item)
        if item == '.git':
            continue
        indent = "    " * level
        if os.path.isdir(item_path):
            tree_str += f"{indent}{item}/\n"
            tree_str += generate_tree(item_path, level + 1)
        else:
            tree_str += f"{indent}{item}\n"
    return tree_str

def save_file_tree(repo_name, repo_path):
    """Saves the directory structure in tree format to a file."""
    tree_str = generate_tree(repo_path)
    tree_file_path = os.path.join(DOWNLOAD_FOLDER, f"{repo_name}_structure.txt")
    with open(tree_file_path, 'w') as f:
        f.write(tree_str)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        github_url = request.form.get("github_url")
        if github_url:
            try:
                repo_name = github_url.rstrip('/').split('/')[-1]
                repo_path = os.path.join(DOWNLOAD_FOLDER, repo_name)
                
                if not os.path.exists(repo_path):
                    # Clone the repository
                    Repo.clone_from(github_url, repo_path)
                    flash(f"Repository '{repo_name}' cloned successfully!", "success")
                    
                    # Save file structure
                    save_file_tree(repo_name, repo_path)
                    flash(f"File structure of '{repo_name}' saved successfully!", "success")
                    
                    # Trigger the external API -------------------------------------------------------------------------
                    send_prompt_request(repo_name)


                    # Redirect to the success page
                    return redirect(url_for("success", repo_name=repo_name))
                else:
                    flash(f"Repository '{repo_name}' already exists in the download folder.", "warning")
            except Exception as e:
                flash(f"Error cloning repository: {e}", "danger")
        else:
            flash("Please provide a valid GitHub URL.", "warning")
        return redirect(url_for("index"))
    
    return render_template("index.html")




@app.route("/success")
def success():
    repo_name = request.args.get('repo_name', '')
    return render_template("projectinfo.html", repo_name=repo_name)

def send_prompt_request(repo_name, extra_text, model="smollm:latest"):
    # Construct the full file path by combining the folder and file name
    file_path = os.path.join('./download/', repo_name)
    url = 'https://70b4-136-233-130-145.ngrok-free.app/api/generate'
    # Read content from the specified file
    with open(file_path, 'r') as file:
        prompt_content = file.read()

    # Combine prompt content with extra text
    full_prompt = prompt_content + extra_text

    # Construct headers if needed
    headers = {
        # Add necessary headers here
    }

    # Prepare data with the combined prompt
    data = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }

    # Send POST request with headers and JSON body
    response = requests.post(url, headers=headers, json=data)

    # Print response details
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    print(full_prompt)


if __name__ == "__main__":
    app.run(debug=True)
