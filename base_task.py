import luigi
import subprocess
import os
import sqlite3
from datetime import datetime
import uuid  # Import the UUID library



class BaseTask(luigi.Task):
    scan_type = luigi.OptionalParameter(default='main')
    scan_id = luigi.Parameter()
    domain = luigi.Parameter()
    save_directory = luigi.Parameter()
    case = luigi.OptionalParameter(default=None)
    task_id = luigi.Parameter(default=str(uuid.uuid4()), significant=False)  # Add a UUID as a parameter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_connect()
        self.insert_initial_status()

    def db_connect(self):
        """ Establish a connection to the database """
        return sqlite3.connect('task_status.db')

    def insert_initial_status(self):
        """ Insert initial PENDING status into the database """
        self.update_status('pending')

    def update_status(self, status, message=''):
        with self.db_connect() as conn:
            cur = conn.cursor()
            # Check if the entry already exists
            cur.execute('''
                SELECT * FROM task_status WHERE task_id = ?
            ''', (self.task_id,))
            exists = cur.fetchone()

            if exists:
                # Update the existing record
                cur.execute('''
                    UPDATE task_status
                    SET status = ?, message = ?, timestamp = ?, type = ?, scan_id = ?
                    WHERE task_id = ?
                ''', (status, message, datetime.now().isoformat(), self.case, self.scan_id, self.task_id))
            else:
                # Insert a new record
                cur.execute('''
                    INSERT INTO task_status (task_id, task_name, domain, status, message, timestamp, type, scan_id, dir)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.task_id, self.task_family, self.domain, status, message, datetime.now().isoformat(), self.case, self.scan_id, self.save_directory))
            conn.commit()

    def update_scan_status(self, new_status):
        """ Update the status in the scans table for a given scan_id """
        with self.db_connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                UPDATE scans
                SET status = ?
                WHERE scan_id = ?
            ''', (new_status, self.scan_id))
            conn.commit()

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
