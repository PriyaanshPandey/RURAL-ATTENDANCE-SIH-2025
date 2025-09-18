from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'attendance.db')

app = Flask(__name__, static_folder='.')
CORS(app)

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        
        # Updated attendance table with timestamp
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     student_id INTEGER,
                     class_id INTEGER,
                     date TEXT NOT NULL,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                     status TEXT NOT NULL,
                     FOREIGN KEY (student_id) REFERENCES students (id),
                     FOREIGN KEY (class_id) REFERENCES classes (id))''')
        
        # Rest of your init_db code remains the same
        c.execute('''CREATE TABLE IF NOT EXISTS classes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS students
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     roll_no TEXT NOT NULL,
                     name TEXT NOT NULL,
                     class_id INTEGER,
                     qr_code TEXT,
                     FOREIGN KEY (class_id) REFERENCES classes (id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS sync_queue
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     operation TEXT NOT NULL,
                     data TEXT NOT NULL,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute("SELECT COUNT(*) FROM classes")
        if c.fetchone()[0] == 0:
            classes = ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5']
            for class_name in classes:
                c.execute("INSERT INTO classes (name) VALUES (?)", (class_name,))
            for class_id in range(1, 6):
                for i in range(1, 6):
                    roll_no = f"{class_id:03d}{i:03d}"
                    name = f"Student {i} from Class {class_id}"
                    qr_code = f"STUDENT_{class_id}_{i}"
                    c.execute("INSERT INTO students (roll_no, name, class_id, qr_code) VALUES (?, ?, ?, ?)",
                             (roll_no, name, class_id, qr_code))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

# Replace get_attendance with this
@app.route('/api/attendance/<int:class_id>', methods=['GET'])
def get_attendance(class_id):
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        
        c.execute('''SELECT s.id, s.roll_no, s.name, a.status, a.timestamp 
                    FROM students s 
                    LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
                    WHERE s.class_id = ?''', (date, class_id))
        
        attendance = []
        for row in c.fetchall():
            status = row[3] if row[3] else 'Absent'
            timestamp = row[4] if row[4] else 'N/A'
            attendance.append({
                'student_id': row[0],
                'roll_no': row[1],
                'name': row[2],
                'status': status,
                'timestamp': timestamp
            })
        
        return jsonify(attendance)
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

# Add these new routes
@app.route('/api/classes', methods=['POST'])
def add_class():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Missing name'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO classes (name) VALUES (?)", (name,))
        conn.commit()
        return jsonify({'id': c.lastrowid, 'message': 'Class added'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        roll_no = data.get('roll_no')
        name = data.get('name')
        class_id = data.get('class_id')
        qr_code = data.get('qr_code')
        
        if not all([roll_no, name, class_id, qr_code]):
            return jsonify({'error': 'Missing fields'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO students (roll_no, name, class_id, qr_code) VALUES (?, ?, ?, ?)",
                 (roll_no, name, class_id, qr_code))
        conn.commit()
        return jsonify({'id': c.lastrowid, 'message': 'Student added'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Rest of your app.py routes remain unchanged
@app.route('/')
def serve_html():
    try:
        return send_from_directory(BASE_DIR, 'attendance.html')
    except Exception as e:
        return jsonify({'error': f'Failed to serve HTML: {str(e)}'}), 500

@app.route('/sw.js')
def serve_sw():
    try:
        return send_from_directory(BASE_DIR, 'sw.js'), 200, {'Content-Type': 'application/javascript'}
    except Exception as e:
        return jsonify({'error': f'Failed to serve service worker: {str(e)}'}), 500

@app.route('/api/classes', methods=['GET'])
def get_classes():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        c.execute("SELECT id, name FROM classes")
        classes = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
        return jsonify(classes)
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/students/<int:class_id>', methods=['GET'])
def get_students(class_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        c.execute("SELECT id, roll_no, name FROM students WHERE class_id = ?", (class_id,))
        students = [{'id': row[0], 'roll_no': row[1], 'name': row[2]} for row in c.fetchall()]
        if students:
            return jsonify(students)
        else:
            return jsonify({'error': 'No students found for this class'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/student/qr/<qr_code>', methods=['GET'])
def get_student_by_qr(qr_code):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        c.execute("SELECT id, roll_no, name, class_id FROM students WHERE qr_code = ?", (qr_code,))
        student = c.fetchone()
        if student:
            student_data = {
                'id': student[0],
                'roll_no': student[1],
                'name': student[2],
                'class_id': student[3]
            }
            return jsonify(student_data)
        else:
            return jsonify({'error': 'Student not found'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/attendance', methods=['POST'])
def submit_attendance():
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        date = data.get('date')
        attendance_data = data.get('attendance', [])
        
        if class_id is None or date is None or not isinstance(attendance_data, list):
            return jsonify({'error': 'Missing or invalid required fields'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        
        c.execute("SELECT id FROM classes WHERE id = ?", (class_id,))
        if not c.fetchone():
            return jsonify({'error': 'Invalid class ID'}), 400
        
        for record in attendance_data:
            student_id = record.get('student_id')
            status = record.get('status')
            
            if not student_id or status not in ['Present', 'Absent']:
                continue
            
            c.execute("SELECT id FROM students WHERE id = ? AND class_id = ?", (student_id, class_id))
            if not c.fetchone():
                continue
            
            c.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?",
                     (student_id, date))
            existing = c.fetchone()
            
            if existing:
                c.execute("UPDATE attendance SET status = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                         (status, existing[0]))
            else:
                c.execute("INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)",
                         (student_id, class_id, date, status))
        
        conn.commit()
        return jsonify({'message': 'Attendance saved successfully'})
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/sync/queue', methods=['POST'])
def add_to_sync_queue():
    try:
        data = request.get_json()
        operation = data.get('operation')
        sync_data = data.get('data')
        
        if not operation or not sync_data:
            return jsonify({'error': 'Missing operation or data'}), 400
        
        if operation not in ['submit_attendance']:
            return jsonify({'error': 'Invalid operation'}), 400
        
        sync_data_json = json.dumps(sync_data)
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        
        c.execute("INSERT INTO sync_queue (operation, data) VALUES (?, ?)",
                 (operation, sync_data_json))
        
        conn.commit()
        return jsonify({'message': 'Added to sync queue'})
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/sync/process', methods=['POST'])
def process_sync_queue():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        c = conn.cursor()
        
        c.execute("SELECT id, operation, data FROM sync_queue ORDER BY timestamp")
        queue_items = c.fetchall()
        
        processed = 0
        for item in queue_items:
            item_id, operation, data = item
            try:
                sync_data = json.loads(data)
                
                if operation == 'submit_attendance':
                    class_id = sync_data.get('class_id')
                    date = sync_data.get('date')
                    attendance_data = sync_data.get('attendance', [])
                    
                    for record in attendance_data:
                        student_id = record.get('student_id')
                        status = record.get('status')
                        
                        if not student_id or status not in ['Present', 'Absent']:
                            continue
                        
                        c.execute("SELECT id FROM students WHERE id = ? AND class_id = ?", (student_id, class_id))
                        if not c.fetchone():
                            continue
                        
                        c.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?",
                                 (student_id, date))
                        existing = c.fetchone()
                        
                        if existing:
                            c.execute("UPDATE attendance SET status = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                                     (status, existing[0]))
                        else:
                            c.execute("INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)",
                                     (student_id, class_id, date, status))
                
                c.execute("DELETE FROM sync_queue WHERE id = ?", (item_id,))
                processed += 1
            except json.JSONDecodeError:
                c.execute("DELETE FROM sync_queue WHERE id = ?", (item_id,))
                processed += 1
                continue
        
        conn.commit()
        return jsonify({'message': f'Processed {processed} items from sync queue'})
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        conn.close()

init_db()  # always run on import

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)