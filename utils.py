import os
import datetime
save_directory = "results"

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
