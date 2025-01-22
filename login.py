from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from git import Repo
from test import generate_tree
from test import save_file_tree
from test import docker_file_creation
import shutil
import subprocess
import stat
import threading
import time

app = Flask(__name__)
app.secret_key = "ugdscg8ey9ec7098scnmc"
task_done = False

# Configure MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "flask_auth"

mysql = MySQL(app)

@app.route("/")
def home():
    if "user" in session:
        # return render_template("index.html", user=session["user"])
        return redirect(url_for("folder_disply"))
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash the password
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        # Check if username already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Username already exists. Please choose another one.", "danger")
        else:
            # Insert new user into the database
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
            mysql.connection.commit()
            cur.close()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Fetch user from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):  # user[2] is the password_hash column
            session["user"] = username
            flash("Login successful!", "success")
            folder_path = os.path.join("download", username)
            os.makedirs(folder_path, exist_ok=True)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))



#----------------------------------------------------------------------------------------------------------------------------
@app.route("/url_form", methods=["GET", "POST"])
def url_form():
    # if "user" in session:
    #     user = session["user"]
    global repo_name
    username = session["user"] 
    if request.method == "POST":
        github_url = request.form.get("github_url")
        if github_url:
            try:
                repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
                # repo_path = os.path.join(DOWNLOAD_FOLDER, repo_name)

                folder_path = os.path.join("download",username, repo_name)
                os.makedirs(folder_path, exist_ok=True)
                repo_path = os.path.join(folder_path, repo_name)

                if not os.path.exists(repo_path):
                    # Clone the repository
                    Repo.clone_from(github_url, repo_path)
                    flash(f"Repository '{repo_name}' cloned successfully!", "success")
                    
                    # Save file structure
                    save_file_tree(repo_name, repo_path, username)
                    flash(f"File structure of '{repo_name}' saved successfully!", "success")
                    
                    # Trigger the external API -------------------------------------------------------------------------
                    # send_prompt_request(repo_name )
                    # send_prompt_request(file_name, extra_text)


                    # Redirect to the success page
                    # return redirect(url_for("info"))
                    return render_template("projectinfo.html")
                else:
                    flash(f"Repository '{repo_name}' already exists in the download folder.", "warning")
            except Exception as e:
                flash(f"Error cloning repository: {e}", "danger")
        else:
            flash("Please provide a valid GitHub URL.", "warning")
        return redirect(url_for("url_form"))
    
    return render_template("index.html", user=session["user"])



#-----------------------------------------------------------------------------------------------------------------------
@app.route("/folder_disply")
def folder_disply():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    name = session["user"]
    main_folder = os.path.join("download", name)

    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    folders = [f for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]
    return render_template("folders.html", folders=folders)




@app.route("/delete/<folder_name>", methods=["POST"])
def delete_folder(folder_name):
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    user_folder = os.path.join("download", session["user"], folder_name)

    if os.path.exists(user_folder):
        try:
            # Change permissions recursively to ensure we can delete everything
            for root, dirs, files in os.walk(user_folder, topdown=False):
                for name in dirs + files:
                    filepath = os.path.join(root, name)
                    os.chmod(filepath, stat.S_IWRITE)  # Make sure we can write/modify
            shutil.rmtree(user_folder)  # Force delete the folder and its contents
            flash(f"Folder '{folder_name}' deleted successfully.", "success")
        except PermissionError:
            flash(f"Permission error deleting folder: {folder_name}", "danger")
        except Exception as e:
            flash(f"Error deleting folder: {e}", "danger")
    else:
        flash(f"Folder '{folder_name}' does not exist.", "warning")

    return redirect(url_for("folder_disply"))  # Stay on the same page


@app.route("/edit/<folder_name>", methods=["GET"])
def edit_folder(folder_name):
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    session['project_name'] = folder_name
    # Render a new page for editing
    return render_template("projectinfo.html", folder_name=folder_name)


#--------------------------------------------PROJECTINFO PAGE--------------------------------------------------------------------

@app.route("/submit", methods=["GET", "POST"])
def submit():
    project_name = session['project_name']
    username = session["user"]
    if request.method == "POST":
        build_commands = request.form["build_commands"]
        ports = request.form["ports"]
        env_var_keys = request.form.getlist("env_var_key[]")
        env_var_values = request.form.getlist("env_var_value[]")
        env_vars = dict(zip(env_var_keys, env_var_values)) 
        # Save the inputs to a text file
        
        folder_path = os.path.join("download", username, project_name)
        file_path = os.path.join(folder_path, "dockerfile_info.txt")

        # Save the inputs to the text file
        with open(file_path, "w") as file:
            file.write(f"Build Commands: {build_commands}\n")
            file.write(f"Ports: {ports}\n")
            file.write(f"Environment Variables: {env_vars}\n")
        
        thread = threading.Thread(target=testing, args=(project_name, username))
        thread.start()
        # return redirect(url_for('index'))
        return render_template("loading.html")
    return render_template("projectinfo.html")






def testing(project_name,username):
    global task_done
    folder_path = os.path.join("download",username, project_name,project_name)
    # os.makedirs(folder_path, exist_ok=True)
    dockerfile_path = os.path.join(folder_path, "Dockerfile")
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write("# Your Dockerfile content goes here")
    
    # docker_file_creation(file_name, extra_text) # calling api from test.py file
    time.sleep(5)  
    print("Testing function completed!")


    task_done = True

@app.route("/status", methods=["GET"])
def status():
    global task_done
    # Check if the task is done using the global variable
    if task_done:
        # Redirect to the test page after the task is done
        return redirect(url_for("test"))
    return "", 204  # Return "no content" if still processing

@app.route("/test")
def test():
    # Render the final page after the task is completed
    return render_template("home.html")

#--------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
