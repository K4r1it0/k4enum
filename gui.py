# app.py
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
import subprocess
import os
import re
from models import Database
from utils import *


app = Flask(__name__)
CORS(app)

@app.route('/scans', methods=['POST'])
def create_scan():
    data = request.get_json()
    scan_type = data.get('type')
    target = data.get('target')

    if is_valid_domain(target):
        run_scan(target, scan_type)
        return jsonify({'message': 'Scan successfully initiated'}), 200
    else:
        return jsonify({'error': 'Invalid domain provided'}), 400

def run_scan(domain, case_type):
    try:
        command = ['python3', 'scan.py', '-d', domain]
        if case_type == 'passive':
            command += ['-t', 'passive']
        elif case_type == 'hybrid':
            command += ['-t', 'hybrid']
        else:
            print(f"Unknown case type: {case_type}")
            return

        subprocess.Popen(command)
        print(f"Command executed: {' '.join(command)}")
        print("Scan initiated successfully.")
    except Exception as e:
        print(f"Error initiating scan: {e}")

@app.route('/scans', methods=['GET'])
def get_scans():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    status = request.args.get('status')
    search = request.args.get('search')

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

    params = []
    domain, tasks, total_count = Database.get_tasks_for_scan(scan_id, params, status, search, page, per_page)
    if domain is None:
        return jsonify({'error': 'No scan found with the given scan ID'}), 404

    task_list = [
        {'task_id': task['task_id'], 'task_name': task['task_name'], 'status': task['status'],
         'type': task['type'], 'updatedAt': task['timestamp']}
        for task in tasks
    ]
    total_pages = (total_count + per_page - 1) // per_page

    return jsonify({
        'domain': domain,
        'data': task_list,
        'pagination': {
            'total_items': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    })

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
    app.run(debug=True, host='0.0.0.0', port=1234)
