# Your luigi tasks file
import luigi
import subprocess
import uuid
from models import Database

class BaseTask(luigi.Task):
    scan_type = luigi.OptionalParameter(default='main')
    scan_id = luigi.Parameter()
    domain = luigi.Parameter()
    save_directory = luigi.Parameter()
    case = luigi.OptionalParameter(default=None)
    task_id = luigi.Parameter(default=str(uuid.uuid4()), significant=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_initial_status()

    def insert_initial_status(self):
        Database.insert_initial_status(self.task_id, self.task_family, self.domain, self.save_directory, self.case, self.scan_id)

    def update_status(self, status, message=''):
        Database.update_status(self.task_id, status, message, self.task_family, self.domain, self.case, self.scan_id, self.save_directory)

    def update_scan_status(self, new_status):
        Database.update_scan_status(self.scan_id, new_status)

    def run_cmd(self, cmd, output_path):
        print(f"Executing command: {cmd}")
        self.update_status('running')
        try:
            with open(output_path, 'w') as file:
                subprocess.run(cmd, shell=True, check=True, stdout=file, stderr=subprocess.STDOUT)
            self.update_status('done')
        except subprocess.CalledProcessError as e:
            with open(output_path, 'w') as file:
                file.write(f"CalledProcessError: {e}")
            self.fail_task(f"Command failed with error: {e}")

    def fail_task(self, message):
        print(message)
        self.update_status('failed', message)
