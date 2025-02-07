from flask import Flask, render_template, request, redirect, url_for, flash
import os
from git import Repo
import requests
import json



app = Flask(__name__)

app.secret_key = 'your_secret_key'
repo_name = None
# Ensure the download directory exists
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def generate_tree(root_path, level=0):
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

def save_file_tree(repo_name, repo_path,username):
    tree_str = generate_tree(repo_path)
    # tree_file_path = os.path.join(DOWNLOAD_FOLDER, f"{repo_name}_structure.txt")
    tree_file_path = os.path.join('download',username, repo_name, f"{repo_name}.txt")

    with open(tree_file_path, 'w') as f:
        f.write(tree_str)



@app.route('/')
def home():
    return render_template("page1.html")

@app.route('/url_form', methods=['POST'])
def url_form():
    global repo_name
    if request.method == "POST":
        github_url = request.form.get("github_url")
        if github_url:
            try:
                repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
                # repo_path = os.path.join(DOWNLOAD_FOLDER, repo_name)

                folder_path = os.path.join("download", repo_name)
                os.makedirs(folder_path, exist_ok=True)
                repo_path = os.path.join(folder_path, repo_name)

                if not os.path.exists(repo_path):
                    # Clone the repository
                    Repo.clone_from(github_url, repo_path)
                    flash(f"Repository '{repo_name}' cloned successfully!", "success")
                    
                    # Save file structure
                    save_file_tree(repo_name, repo_path)
                    flash(f"File structure of '{repo_name}' saved successfully!", "success")
                    
                    # Trigger the external API -------------------------------------------------------------------------
                    # send_prompt_request(repo_name )
                    # send_prompt_request(file_name, extra_text)


                    # Redirect to the success page
                    return redirect(url_for("info"))
                else:
                    flash(f"Repository '{repo_name}' already exists in the download folder.", "warning")
            except Exception as e:
                flash(f"Error cloning repository: {e}", "danger")
        else:
            flash("Please provide a valid GitHub URL.", "warning")
        return redirect(url_for("url_form"))
    
    return render_template("index.html")

@app.route('/info', methods=['GET'])
def info():
    return render_template("projectinfo.html")


#-----------------------------------projectinfo page ------------------------------------------------------------------

@app.route("/projectinfo", methods=["GET", "POST"])
def projectinfo():
    if request.method == "POST":
        build_commands = request.form["build_commands"]
        ports = request.form["ports"]
        env_var_keys = request.form.getlist("env_var_key[]")
        env_var_values = request.form.getlist("env_var_value[]")
        env_vars = dict(zip(env_var_keys, env_var_values)) 

        # Save the inputs to a text file
        with open("dockerfile_info.txt", "w") as file:

            file.write(f"Build Commands: {build_commands}\n")
            file.write(f"Ports: {ports}\n")

            file.write(f"Environment Variables: {env_vars}\n")
        
        return redirect(url_for('index'))

    return render_template("projectinfo.html")




if __name__ == "__main__":
    app.run(debug=True)
