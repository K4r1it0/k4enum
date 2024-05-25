import sqlite3
from datetime import datetime

DATABASE_PATH = 'task_status.db'

class Database:
    @staticmethod
    def connect():
        """ Establish a connection to the database """
        return sqlite3.connect(DATABASE_PATH)

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
    def update_status(task_id, status, message, task_family, domain, case, scan_id, save_directory):
        timestamp = datetime.now().isoformat()
        with Database.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT * FROM task_status WHERE task_id = ?
            ''', (task_id,))
            exists = cur.fetchone()

            if exists:
                cur.execute('''
                    UPDATE task_status
                    SET status = ?, message = ?, timestamp = ?, type = ?, scan_id = ?
                    WHERE task_id = ?
                ''', (status, message, timestamp, case, scan_id, task_id))
            else:
                cur.execute('''
                    INSERT INTO task_status (task_id, task_name, domain, status, message, timestamp, type, scan_id, dir)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (task_id, task_family, domain, status, message, timestamp, case, scan_id, save_directory))
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
	            'createdAt': scan[3],
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
            if task['status'] in task_counts:
                task_counts[task['status']] = task['count']
        
        total_tasks = total_result['total'] if total_result else 0
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

        total_scans = total_result['total'] if total_result else 0
        possible_statuses = ['done', 'failed', 'running', 'pending']
        scan_counts_dict = {status: 0 for status in possible_statuses}
        for scan in scans:
            if scan['status'] in scan_counts_dict:
            	scan_counts_dict[scan['status']] = scan['count']

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
            domain = domain_result['domain'] if domain_result else None
            if not domain:
                return None, None

            params.extend([scan_id, 'MainEnumerationTask', 'YieldWrapper', 'Miscellaneous'])
            if status:
                base_query += ' AND status = ?'
                params.append(status)
            if search:
                base_query += ' AND task_name LIKE ?'
                params.append(f"%{search}%")

            base_query += ' ORDER BY timestamp DESC'
            
            total_count = Database.get_total_count(base_query, params)
            paginated_query = Database.paginate_query(base_query, page, per_page)
            tasks = conn.execute(paginated_query, params).fetchall()
        
        return domain, tasks, total_count

    @staticmethod
    def get_total_count(query, params):
        """ Get the total count for a query """
        count_query = f"SELECT COUNT(*) AS total FROM ({query})"
        with Database.connect() as conn:
            total_count = conn.execute(count_query, params).fetchone()['total']
        
        return total_count

    @staticmethod
    def paginate_query(query, page, per_page):
        """ Paginate a query """
        offset = (page - 1) * per_page
        return f"{query} LIMIT {per_page} OFFSET {offset}"
