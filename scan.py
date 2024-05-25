import argparse
import luigi
import logging
import sqlite3
import uuid
from datetime import datetime

from luigi_tasks import MainEnumerationTask
from database import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_enumeration_tasks(domain, scan_type):
    scan_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    save_directory = create_directory(domain)
    
    try:
        Database.insert_scan(scan_id, domain, scan_type, timestamp, 'running')
        logging.info(f"Inserted scan record: {scan_id}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return
    
    # Build tasks linked to this scan
    luigi.build([MainEnumerationTask(scan_type=scan_type, domain=domain, save_directory=save_directory, scan_id=scan_id)], workers=50, local_scheduler=True)
    logging.info("Luigi tasks have been built and are running.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run enumeration tasks on a given domain.')
    parser.add_argument('-domain', '-d', required=True, help='The domain to run tasks against.')
    parser.add_argument('-type', '-t', required=True, help='The type of the scan')
    args = parser.parse_args()

    if args.domain and args.type:
        run_enumeration_tasks(args.domain, args.type)
    else:
        logging.warning("Missing required arguments. Please provide both a domain and a scan type.")
