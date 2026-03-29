from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models.db import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 🔐 ADMIN REQUIRED (ROLE-BASED) with better error handling
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != "admin":
            flash("Access denied. Admin privileges required.", "danger")
            # If user is logged in but not admin, send them to teacher dashboard
            if session.get('logged_in'):
                return redirect(url_for('main.index'))
            # Otherwise send to login page
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapper


# 🔁 /admin → dashboard
@admin_bp.route('/')
@admin_required
def admin_home():
    return redirect(url_for('admin.admin_dashboard'))


# 📊 DASHBOARD
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search = (request.args.get('search') or '').strip().lower()

    if search:
        sql = """
        SELECT * FROM students
        WHERE LOWER(first_name) LIKE %s
        OR LOWER(last_name) LIKE %s
        OR LOWER(father_name) LIKE %s
        OR sr_no = %s
        """

        sr_no_val = int(search) if search.isdigit() else -1

        cursor.execute(sql, (
            search + '%',
            search + '%',
            search + '%',
            sr_no_val
        ))
    else:
        cursor.execute("SELECT * FROM students ORDER BY sr_no")

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', students=students, search=search)


# ➕ ADD STUDENT
@admin_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def admin_add():

    if request.method == 'POST':

        conn = get_db_connection()
        cursor = conn.cursor()

        def safe_int(val): return int(val) if val and val.strip() else 0
        def safe_float(val): return float(val) if val and val.strip() else 0.0

        cursor.execute("SELECT MAX(sr_no) FROM students")
        new_id = (cursor.fetchone()[0] or 0) + 1

        data = (
            new_id,
            request.form.get('Last_Name') or '',
            request.form.get('First_Name') or '',
            request.form.get('Father_Name') or '',
            request.form.get('Mother_Name') or '',
            request.form.get('DOB') or None,
            request.form.get('Category') or '',
            request.form.get('SubCategory_Flag') or '',
            request.form.get('Exam') or '',
            request.form.get('Seat_No') or '',
            safe_float(request.form.get('Percentage')),
            request.form.get('Passing_Month_Year') or '',
            safe_int(request.form.get('ID1')),
            safe_int(request.form.get('ID2')),
            safe_int(request.form.get('ID3')),
            safe_int(request.form.get('Score1')),
            safe_int(request.form.get('Score2')),
            safe_int(request.form.get('Score3')),
        )

        cursor.execute("""
        INSERT INTO students VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)

        conn.commit()
        cursor.close()
        conn.close()

        flash("Student added successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin_add.html')


# ✏️ EDIT STUDENT
@admin_bp.route('/edit/<int:sr_no>', methods=['GET', 'POST'])
@admin_required
def admin_edit(sr_no):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        def safe_int(val): return int(val) if val and val.strip() else 0
        def safe_float(val): return float(val) if val and val.strip() else 0.0

        sql = """
        UPDATE students SET
            last_name=%s, first_name=%s, father_name=%s, mother_name=%s,
            dob=%s, category=%s, subcategory_flag=%s,
            exam=%s, seat_no=%s, percentage=%s,
            passing_month_year=%s, id1=%s, id2=%s, id3=%s,
            score1=%s, score2=%s, score3=%s
        WHERE sr_no=%s
        """

        values = (
            request.form.get('Last_Name') or '',
            request.form.get('First_Name') or '',
            request.form.get('Father_Name') or '',
            request.form.get('Mother_Name') or '',
            request.form.get('DOB') or None,
            request.form.get('Category') or '',
            request.form.get('SubCategory_Flag') or '',
            request.form.get('Exam') or '',
            request.form.get('Seat_No') or '',
            safe_float(request.form.get('Percentage')),
            request.form.get('Passing_Month_Year') or '',
            safe_int(request.form.get('ID1')),
            safe_int(request.form.get('ID2')),
            safe_int(request.form.get('ID3')),
            safe_int(request.form.get('Score1')),
            safe_int(request.form.get('Score2')),
            safe_int(request.form.get('Score3')),
            sr_no
        )

        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        flash("Student updated successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    cursor.execute("SELECT * FROM students WHERE sr_no=%s", (sr_no,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('admin_edit.html', student=student)


# ❌ DELETE
@admin_bp.route('/delete/<int:sr_no>')
@admin_required
def admin_delete(sr_no):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE sr_no=%s", (sr_no,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))


# 🚪 LOGOUT
@admin_bp.route('/logout')
def admin_logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))
