from flask import Flask, jsonify, request, send_from_directory, abort
import sqlite3
from flask_cors import CORS
import subprocess
import os
import re
app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('task_status.db')
    conn.row_factory = sqlite3.Row
    return conn

def paginate_query(query, page, per_page):
    offset = (page - 1) * per_page
    paginated_query = query + f" LIMIT {per_page} OFFSET {offset}"
    return paginated_query

def get_total_count(query, conn, params=None):
    # Modify query to count rows instead of fetching data
    count_query = "SELECT COUNT(*) AS total FROM (" + query + ")"
    if params:
        total = conn.execute(count_query, params).fetchone()['total']
    else:
        total = conn.execute(count_query).fetchone()['total']
    return total


def is_valid_domain(domain):
    # Regular expression pattern to match a valid domain
    domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(domain_pattern, domain)


@app.route('/scans', methods=['POST'])
def create_scan():
    # Extract type and target from the request
    data = request.get_json()
    scan_type = data.get('type')
    target = data.get('target')

    # Check if the domain is valid
    if is_valid_domain(target):
        run_scan(target, scan_type)
        return jsonify({'message': 'Scan successfully initiated'}), 200
    else:
        return jsonify({'error': 'Invalid domain provided'}), 400


def run_scan(domain, case_type):
    try:
        # Start constructing the command with the script, domain, and type
        command = ['python3', 'scan.py', '-d', domain]

        # Determine which type of scan to run
        if case_type == 'passive':
            command += ['-t', 'passive']
        elif case_type == 'hybrid':
            command += ['-t', 'hybrid']
        else:
            print(f"Unknown case type: {case_type}")
            return

        # Execute the scan.py script with the domain and type arguments
        subprocess.Popen(command)
        print(f"Command executed: {' '.join(command)}")
        print("Scan initiated successfully.")
    except Exception as e:
        # Handle any errors that occur during the subprocess execution
        print(f"Error initiating scan: {e}")

@app.route('/scans', methods=['GET'])
def get_scans():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    status = request.args.get('status')
    search = request.args.get('search')
    
    conn = get_db_connection()
    base_query = '''
        SELECT scan_id, scan_type, domain, timestamp, status
        FROM scans
    '''
    where_clauses = []
    params = []
    if status:
        where_clauses.append("status = ?")
        params.append(status)
    if search:
        where_clauses.append("domain LIKE ?")
        params.append(f"%{search}%")

    if where_clauses:
        base_query += ' WHERE ' + ' AND '.join(where_clauses)
    
    base_query += ' ORDER BY timestamp DESC'
    
    total_count = get_total_count(base_query, conn, params)
    paginated_query = paginate_query(base_query, page, per_page)
    scans = conn.execute(paginated_query, params).fetchall()
    conn.close()
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
    conn = get_db_connection()
    status_query = '''
        SELECT status, COUNT(*) AS count
        FROM task_status
        WHERE scan_id = ?
        GROUP BY status
    '''
    total_query = '''
        SELECT COUNT(*) AS total
        FROM task_status
        WHERE scan_id = ?
    '''

    # Execute the queries
    tasks = conn.execute(status_query, (scan_id,)).fetchall()
    total_result = conn.execute(total_query, (scan_id,)).fetchone()
    conn.close()

    # Initialize a dictionary for task counts with all required statuses set to zero
    task_counts = {'failed': 0, 'running': 0, 'pending': 0, 'done': 0}

    # Update the dictionary with actual counts from the database
    for task in tasks:
        if task['status'] in task_counts:
            task_counts[task['status']] = task['count']

    # Calculate the total count of tasks for the scan_id
    total_tasks = total_result['total'] if total_result else 0

    # Append the total count to the task counts
    task_counts['all'] = total_tasks

    # Create a list from the dictionary to format the output as a list of dictionaries
    status_counts = [{'status': status, 'count': count} for status, count in task_counts.items()]

    return jsonify({
        'status_counts': status_counts
    })



@app.route('/scans/count', methods=['GET'])
def count_scans():
    conn = get_db_connection()
    status_query = '''
        SELECT status, COUNT(*) AS count
        FROM scans
        GROUP BY status
    '''
    total_query = '''
        SELECT COUNT(*) AS total
        FROM scans
    '''

    # Execute the queries
    scans = conn.execute(status_query).fetchall()
    total_result = conn.execute(total_query).fetchone()
    conn.close()

    # Calculate the total count of scans
    total_scans = total_result['total'] if total_result else 0

    # Define all possible statuses
    possible_statuses = ['done', 'failed', 'running', 'pending']  # Add 'pending' if it's also a required status
    scan_counts_dict = {status: 0 for status in possible_statuses}  # Initialize counts to zero

    # Update counts from the database
    for scan in scans:
        if scan['status'] in scan_counts_dict:
            scan_counts_dict[scan['status']] = scan['count']

    # Prepare the list to return
    scan_counts = [{'status': status, 'count': scan_counts_dict[status]} for status in possible_statuses]

    scan_counts.append({'status':"all","count":total_scans})

    return jsonify({
        'status_counts': scan_counts
    })

@app.route('/scans/<scan_id>/tasks', methods=['GET'])
def get_tasks_for_scan(scan_id):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    status = request.args.get('status')
    search = request.args.get('search')

    conn = get_db_connection()
    # Retrieve domain from the scans table
    domain_query = 'SELECT domain FROM scans WHERE scan_id = ?'
    domain_result = conn.execute(domain_query, (scan_id,)).fetchone()
    domain = domain_result['domain'] if domain_result else None

    if not domain:
        return jsonify({'error': 'No scan found with the given scan ID'}), 404

    # Query tasks related to the scan_id
    base_query = f'''
        SELECT task_id, task_name, status, type, message, timestamp
        FROM task_status
        WHERE scan_id = ?
    '''
    params = [scan_id]
    if status:
        base_query += ' AND status = ?'
        params.append(status)
    if search:
        base_query += ' AND task_name LIKE ?'
        params.append(f"%{search}%")

    base_query += ' ORDER BY timestamp DESC'
    
    total_count = get_total_count(base_query, conn, params)
    paginated_query = paginate_query(base_query, page, per_page)
    tasks = conn.execute(paginated_query, params).fetchall()
    conn.close()
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
    conn = get_db_connection()
    try:
        # Query to retrieve directory, task_name, and type using task_id
        task_query = 'SELECT dir, task_name, type FROM task_status WHERE task_id = ?'
        task = conn.execute(task_query, (task_id,)).fetchone()
        if task and task['dir'] and task['task_name'] and task['type']:
            directory = task['dir']
            file_name = f"{task['task_name']}-{task['type']}"
            # Here we are just forming a path, assuming the file has a known extension. You need to manage this based on your files.
            file_path = os.path.join(directory, f"{file_name}")  # Replace '.extension' with your actual file extension

            # Check if file exists before attempting to send it
            if os.path.exists(file_path):
                return send_from_directory(directory, f"{file_name}", as_attachment=True)
            else:
                abort(404, description="File not found")
        else:
            abort(404, description="Task not found or incomplete data")
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1234)
