import subprocess
import time
import os

# Path to the Dockerfile directory
# Path to the error log file
# error_log_file = "error.txt"

# Function to build the Docker image
def build_docker_image(username,project_name):
    file_path = os.path.abspath(os.path.join('./download/', username, project_name, project_name ))
    error_file_path = os.path.abspath(os.path.join('./download/', username, project_name, 'error.txt'  ))
    try:
        # Run the docker build command
        result = subprocess.run(
            ["docker", "build", "-t", "my_image", file_path],
            capture_output=True,
            text=True
        )

        # Check if the build was successful
        if result.returncode == 0:
            print("Docker image built successfully.")
            with open(error_file_path, "w") as f:
                f.write("DONE\n")
            return True
        else:
            # Log the error output
            with open(error_file_path, "w") as f:
                f.write(f"Error: {result.stderr}\n")
            print("Error encountered. Check error.txt for details.")
            return False

    except Exception as e:
        # Log any unexpected exceptions
        with open(error_file_path, "w") as f:
            f.write(f"Unexpected error: {str(e)}\n")
        print("Unexpected error encountered. Check error.txt for details.")
        return False

# Main loop to attempt building the Docker image
# while True:
#     success = build_docker_image()
#     if success:
#         break
#     else:
#         print("Retrying in 5 seconds...")
#         time.sleep(5)
