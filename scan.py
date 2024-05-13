import argparse
import luigi
import luigi.configuration
import logging
import sqlite3
import uuid
from datetime import datetime
from tasks import MainEnumerationTask
from utils import create_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_enumeration_tasks(domain, scan_type):
    scan_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    save_directory = create_directory(domain)
    
    try:
        conn = sqlite3.connect('task_status.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO scans (scan_id, domain, scan_type, timestamp, status) VALUES (?, ?, ?, ?, ?)
        ''', (scan_id, domain, scan_type, timestamp, 'running'))
        conn.commit()
        conn.close()
        logging.info(f"Inserted scan record: {scan_id}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return
    
    # Build tasks linked to this scan
    luigi.build([MainEnumerationTask(scan_type=scan_type, domain=domain, save_directory=save_directory, scan_id=scan_id)], workers=50, local_scheduler=True)
    logging.info("Luigi tasks have been built and are running.")

def setup_database():
    try:
        connection = sqlite3.connect('task_status.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                domain TEXT,
        status TEXT,
                scan_type TEXT,
                timestamp TEXT
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                task_name TEXT,
                status TEXT,
                message TEXT,
                timestamp TEXT,
                scan_id TEXT,
                type TEXT,
                process_pid,
                dir TEXT,
                domain Text,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
            );
        ''')
        connection.commit()
        connection.close()
        logging.info("Database setup complete.")
    except sqlite3.Error as e:
        logging.error(f"Failed to set up database: {e}")

if __name__ == "__main__":
    setup_database()
    luigi.interface.core.log_level = 'DEBUG'
    
    parser = argparse.ArgumentParser(description='Run enumeration tasks on a given domain.')
    parser.add_argument('-domain', '-d', required=True, help='The domain to run tasks against.')
    parser.add_argument('-type', '-t', required=True, help='The type of the scan')
    args = parser.parse_args()

    if args.domain and args.type:
        run_enumeration_tasks(args.domain, args.type)
    else:
        logging.warning("Missing required arguments. Please provide both a domain and a scan type.")
