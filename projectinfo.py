from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route to render the form and collect inputs
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        build_commands = request.form["build_commands"]
        ports = request.form["ports"]
        env_var_keys = request.form.getlist("env_var_key[]")
        env_var_values = request.form.getlist("env_var_value[]")
        env_vars = dict(zip(env_var_keys, env_var_values))  # Combine them into a dictionary


        # Save the inputs to a text file
        with open("dockerfile_info.txt", "w") as file:

            file.write(f"Build Commands: {build_commands}\n")
            file.write(f"Ports: {ports}\n")

            file.write(f"Environment Variables: {env_vars}\n")
        
        return redirect(url_for('index'))

    return render_template("projectinfo.html")

if __name__ == "__main__":
    app.run(debug=True)
