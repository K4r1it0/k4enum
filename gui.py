from flask import Flask, jsonify, request, send_from_directory, abort
from tasks import MainEnumerationTask
from flask_cors import CORS
from datetime import datetime as dt
from multiprocessing import Process
import sqlite3
from models import Database
from utils import *
import subprocess
import uuid
import os
import re
import luigi
import logging


app = Flask(__name__)
CORS(app)

@app.route('/scans', methods=['POST'])
def create_scan():
    data = request.json
    target = data.get('target')
    scan_type = data.get('type')
    
    if not is_valid_domain(target):
        return 'Invalid domain', 400
    
    # Start a new process to run the enumeration tasks
    p = Process(target=run_enumeration_tasks, args=(target, scan_type))
    p.start()
    
    return 'Scan started successfully'

def run_enumeration_tasks(domain, scan_type):
    scan_id = str(uuid.uuid4())
    timestamp = dt.now().isoformat()
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

@app.route('/scans', methods=['GET'])
def get_scans():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    status = request.args.get('status')
    search = request.args.get('search')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    params = []
    scans, total_count = Database.get_scans(params, status, search, page, per_page)
    scan_list = [
        {'scan_id': scan['scan_id'], 'scan_type': scan['scan_type'], 'domain': scan['domain'],
         'createdAt': scan['timestamp'], 'status': scan['status']}
        for scan in scans
    ]
    total_pages = (total_count + per_page - 1) // per_page
    return jsonify({
        'data': scan_list,
        'pagination': {
            'total_items': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    })

@app.route('/scans/<scan_id>/tasks/count', methods=['GET'])
def count_tasks_by_scan(scan_id):
    status_counts = Database.count_tasks_by_scan(scan_id)
    return jsonify({'status_counts': status_counts})

@app.route('/scans/count', methods=['GET'])
def count_scans():
    scan_counts = Database.count_scans()
    return jsonify({'status_counts': scan_counts})

@app.route('/scans/<scan_id>/tasks', methods=['GET'])
def get_tasks_for_scan(scan_id):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    status = request.args.get('status')
    search = request.args.get('search')

    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    params = []
    result = Database.get_tasks_for_scan(scan_id, page, per_page, status, search)
    if result['domain'] is None:
        return jsonify({'error': 'No scan found with the given scan ID'}), 404

    return jsonify(result)



@app.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    task = Database.get_task_details(task_id)
    if not task or not task['dir'] or not task['task_name'] or not task['type']:
        abort(404, description="Task not found or incomplete data")

    directory = task['dir']
    file_name = f"{task['task_name']}-{task['type']}"
    file_path = os.path.join(directory, file_name)

    if not os.path.exists(file_path):
        abort(404, description="File not found")

    return send_from_directory(directory, file_name, as_attachment=True)

if __name__ == '__main__':
    Database.create_tables()
    app.run(debug=True, host='0.0.0.0', port=1234)
