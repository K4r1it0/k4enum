import os
import datetime
import re
from flask import send_from_directory, abort
from models import Database
save_directory = "results"


def download_file(task_id):
    task = Database.get_task_details(task_id)
    if task and task[0] and task[1] and task[2]:
        directory, task_name, task_type = task
        file_name = f"{task_name}-{task_type}"
        file_path = os.path.join(directory, file_name)  # Adjust as needed for your file extension

        if os.path.exists(file_path):
            return send_from_directory(directory, file_name, as_attachment=True)
        else:
            abort(404, description="File not found")
    else:
        abort(404, description="Task not found or incomplete data")

def is_valid_domain(domain):
    """Check if the provided domain is valid."""
    # Use a regex pattern to validate the domain
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, domain) is not None


def create_directory(dir_name):
    current_dir = os.getcwd()
    # Get the current date and time in the format YYYY-MM-DD-HH-MM-SS
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Combine the directory name with the current date and time
    dir_with_datetime = f"{dir_name}-{current_datetime}"
    dir_path = os.path.join(current_dir, save_directory, dir_with_datetime)

    try:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Directory '{dir_path}' created ")
        return dir_path
    except OSError as error:
        print(f"Creation of the directory '{dir_path}' failed due to: {error}")
        return False


def merge_results(save_directory):
    tasks = ["PassiveAssetDiscoveryV1", "PassiveAssetDiscoveryV2", "HTTPProbing", "TlsGrabber", "CNAMEChecker", "PortScaning", "TlsFilter", "VulnerabilityScanner", "PrototypePollution", "PortScaning"]
    cases = ["passive", "active"]
    for task in tasks:
        final_output_path = f"{save_directory}/{task}.txt"
        with open(final_output_path, 'w') as final_file:
            for case in cases:
                input_file_path = f"{save_directory}/{task}-{case}"
                
                try:
                    with open(input_file_path, 'r') as input_file:
                        # Directly write the content without adding newlines
                        content = input_file.read()
                        # Ensure there's no newline at the end of the content to avoid adding extra space
                        content = content.rstrip('\n')
                        final_file.write(content)
                        # Add a newline to separate the current content from the next one, if any
                        final_file.write('\n')  # This ensures the next content starts on a new line, if any
                except FileNotFoundError:
                    print(f"Warning: File not found {input_file_path}, skipping.")        
        print(f"Merged results saved to {final_output_path}")
