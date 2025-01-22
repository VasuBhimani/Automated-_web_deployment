from flask import Flask, render_template, request, redirect, url_for
from app import repo_name

app = Flask(__name__)
# Route to render the form and collect inputs
@app.route("/sumbit", methods=["GET", "POST"])
def index():
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



#----------------------------------------finding package.json file------------------------------------------------------------

def find_and_read_package_files(directory):
    package_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file == "package.json":  # Look specifically for 'package.json'
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = json.load(f)  # Parse JSON content
                        package_files.append({
                            "path": file_path,
                            "content": content  # Store both path and content
                        })
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {file_path}: {e}")

    return package_files

# Example usage
project_directory = "mernProjectEcommerce-master"  # Replace with the path to your project directory
# found_packages = find_and_read_package_files(project_directory)

# print(found_packages)


#--------------------------------------calling API----------------------------------------------------------------------------
def send_prompt_request(file_name, extra_text):
    file_path = os.path.join('./download/', file_name)
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


file_name = 'AWS_SCD_booth.git_structure.txt' 
extra_text = "create production ready docker file for this file structure and just create docker file dont give me other explaination or comments and without markdown"
# extra_text = ""

# send_prompt_request(file_name, extra_text)

#-------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
