import sqlite3
from datetime import datetime

DATABASE_PATH = 'task_status.db'

class Database:
    @staticmethod
    def connect():
        """Establish a connection to the database."""
        return sqlite3.connect(DATABASE_PATH)

    @staticmethod
    def create_tables():
        """Create tables if they do not exist."""
        with Database.connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS task_status (
                    task_id TEXT PRIMARY KEY,
                    task_name TEXT,
                    domain TEXT,
                    status TEXT,
                    message TEXT,
                    timestamp TEXT,
                    type TEXT,
                    scan_id TEXT,
                    dir TEXT,
                    results TEXT,
                    hasOutput BOOLEAN
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    scan_id TEXT PRIMARY KEY,
                    scan_type TEXT,
                    domain TEXT,
                    timestamp TEXT,
                    status TEXT
                )
            ''')
            conn.commit()

    @staticmethod
    def insert_scan(scan_id, domain, scan_type, timestamp, status):
        """Insert a new scan record into the database."""
        with Database.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO scans (scan_id, domain, scan_type, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (scan_id, domain, scan_type, timestamp, status))
            conn.commit()

    @staticmethod
    def get_task_details(task_id):
        """Fetch directory, task_name, and type for a given task_id."""
        query = 'SELECT dir, task_name, type FROM task_status WHERE task_id = ?'
        with Database.connect() as conn:
            task = conn.execute(query, (task_id,)).fetchone()
            if task:
                return {'dir': task[0], 'task_name': task[1], 'type': task[2]}
        return None

    @staticmethod
    def insert_initial_status(task_id, task_family, domain, save_directory, case, scan_id):
        status = 'pending'
        timestamp = datetime.now().isoformat()
        with Database.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO task_status (task_id, task_name, domain, status, message, timestamp, type, scan_id, dir)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, task_family, domain, status, '', timestamp, case, scan_id, save_directory))
            conn.commit()

    @staticmethod
    def update_status(task_id, status, message, task_family, domain, case, scan_id, save_directory, results=None, has_output=False):
        timestamp = datetime.now().isoformat()
        with Database.connect() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM task_status WHERE task_id = ?', (task_id,))
            exists = cur.fetchone()

            if exists:
                cur.execute('''
                    UPDATE task_status
                    SET status = ?, message = ?, timestamp = ?, type = ?, scan_id = ?, results = ?, hasOutput = ?
                    WHERE task_id = ?
                ''', (status, message, timestamp, case, scan_id, results, has_output, task_id))
            else:
                cur.execute('''
                    INSERT INTO task_status (task_id, task_name, domain, status, message, timestamp, type, scan_id, dir, results, hasOutput)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (task_id, task_family, domain, status, message, timestamp, case, scan_id, save_directory, results, has_output))
            conn.commit()

    @staticmethod
    def update_scan_status(scan_id, new_status):
        with Database.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                UPDATE scans
                SET status = ?
                WHERE scan_id = ?
            ''', (new_status, scan_id))
            conn.commit()

    @staticmethod
    def get_scans(params, status, search, page, per_page):
        """ Get paginated scan results based on status and search """
        base_query = '''
            SELECT scan_id, scan_type, domain, timestamp, status
            FROM scans
        '''
        where_clauses = []
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        if search:
            where_clauses.append("domain LIKE ?")
            params.append(f"%{search}%")

        if where_clauses:
            base_query += ' WHERE ' + ' AND '.join(where_clauses)

        base_query += ' ORDER BY timestamp DESC'
        
        total_count = Database.get_total_count(base_query, params)
        paginated_query = Database.paginate_query(base_query, page, per_page)
        with Database.connect() as conn:
            scans = conn.execute(paginated_query, params).fetchall()

        # Convert each tuple to a dictionary for JSON serialization
        scan_list = []
        for scan in scans:
            scan_dict = {
                'scan_id': scan[0],
                'scan_type': scan[1],
                'domain': scan[2],
                'timestamp': scan[3],
                'status': scan[4]
            }
            scan_list.append(scan_dict)
        
        return scan_list, total_count

    @staticmethod
    def count_tasks_by_scan(scan_id):
        """ Count tasks by scan ID """
        excluded_tasks = ('MainEnumerationTask', 'YieldWrapper', 'Miscellaneous')
        status_query = '''
            SELECT status, COUNT(*) AS count
            FROM task_status
            WHERE scan_id = ? AND task_name NOT IN (?, ?, ?)
            GROUP BY status
        '''
        total_query = '''
            SELECT COUNT(*) AS total
            FROM task_status
            WHERE scan_id = ? AND task_name NOT IN (?, ?, ?)
        '''
        with Database.connect() as conn:
            tasks = conn.execute(status_query, (scan_id,) + excluded_tasks).fetchall()
            total_result = conn.execute(total_query, (scan_id,) + excluded_tasks).fetchone()
        
        task_counts = {'failed': 0, 'running': 0, 'pending': 0, 'done': 0}
        for task in tasks:
            if task[0] in task_counts:
                task_counts[task[0]] = task[1]
        
        total_tasks = total_result[0] if total_result else 0
        task_counts['all'] = total_tasks

        return [{'status': status, 'count': count} for status, count in task_counts.items()]

    @staticmethod
    def count_scans():
        """ Count scans by status """
        status_query = '''
            SELECT status, COUNT(*) AS count
            FROM scans
            GROUP BY status
        '''
        total_query = '''
            SELECT COUNT(*) AS total
            FROM scans
        '''
        with Database.connect() as conn:
            scans = conn.execute(status_query).fetchall()
            total_result = conn.execute(total_query).fetchone()

        total_scans = total_result[0] if total_result else 0
        possible_statuses = ['done', 'failed', 'running', 'pending']
        scan_counts_dict = {status: 0 for status in possible_statuses}
        for scan in scans:
            if scan[0] in scan_counts_dict:
                scan_counts_dict[scan[0]] = scan[1]

        scan_counts = [{'status': status, 'count': scan_counts_dict[status]} for status in possible_statuses]
        scan_counts.append({'status': "all", 'count': total_scans})
        return scan_counts

    @staticmethod
    def get_tasks_for_scan(scan_id, params, status, search, page, per_page):
        """ Get paginated tasks for a scan based on status and search """
        domain_query = 'SELECT domain FROM scans WHERE scan_id = ?'
        base_query = '''
            SELECT task_id, task_name, status, type, message, timestamp
            FROM task_status
            WHERE scan_id = ? AND task_name NOT IN (?, ?, ?)
        '''
        with Database.connect() as conn:
            domain_result = conn.execute(domain_query, (scan_id,)).fetchone()
            domain = domain_result[0] if domain_result else None

        params.append(scan_id)
        excluded_tasks = ('MainEnumerationTask', 'YieldWrapper', 'Miscellaneous')
        params.extend(excluded_tasks)
        where_clauses = []
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        if search:
            where_clauses.append("task_name LIKE ?")
            params.append(f"%{search}%")

        if where_clauses:
            base_query += ' AND ' + ' AND '.join(where_clauses)

        base_query += ' ORDER BY timestamp DESC'
        
        total_count = Database.get_total_count(base_query, params)
        paginated_query = Database.paginate_query(base_query, page, per_page)
        with Database.connect() as conn:
            tasks = conn.execute(paginated_query, params).fetchall()

        # Convert each tuple to a dictionary for JSON serialization
        task_list = []
        for task in tasks:
            task_dict = {
                'task_id': task[0],
                'task_name': task[1],
                'status': task[2],
                'type': task[3],
                'message': task[4],
                'timestamp': task[5],
                'domain': domain
            }
            task_list.append(task_dict)
        
        return task_list, total_count

    @staticmethod
    def get_total_count(query, params):
        """ Get total count of rows for a given query and parameters """
        count_query = f'SELECT COUNT(*) FROM ({query})'
        with Database.connect() as conn:
            total_result = conn.execute(count_query, params).fetchone()
        return total_result[0] if total_result else 0

    @staticmethod
    def paginate_query(query, page, per_page):
        """ Add pagination to a query """
        offset = (page - 1) * per_page
        return f'{query} LIMIT {per_page} OFFSET {offset}'
