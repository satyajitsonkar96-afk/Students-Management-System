from flask import Blueprint, render_template, request, redirect, url_for, session, flash   # Import Flask modules for routing, rendering, request handling, redirects, URL building, session management, and flash messages
from functools import wraps                     # Import wraps decorator to preserve metadata of wrapped functions
from models.db import get_db_connection         # Import the database connection helper from the db module

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')   # Create a Blueprint named 'admin' with URL prefix '/admin'

# 🔐 ADMIN REQUIRED (ROLE-BASED) with better error handling
def admin_required(f):                          # Define a decorator function that restricts access to admin users only
    @wraps(f)                                   # Use wraps to preserve the original function's name and docstring
    def wrapper(*args, **kwargs):               # Define the wrapper function that will replace the original
        if not session.get('logged_in') or session.get('role') != "admin":   # Check if user is not logged in or role is not admin
            flash("Access denied. Admin privileges required.", "danger")     # Flash an error message with category 'danger'
            # If user is logged in but not admin, send them to teacher dashboard
            if session.get('logged_in'):        # If user is logged in (but not admin)
                return redirect(url_for('main.index'))   # Redirect to main index (non-admin dashboard)
            # Otherwise send to login page
            return redirect(url_for('main.login'))       # Redirect to login page if not logged in
        return f(*args, **kwargs)               # If admin, call the original function
    return wrapper                              # Return the wrapper function

# 🔁 /admin → dashboard
@admin_bp.route('/')                            # Register a route for '/admin/' (default admin URL)
@admin_required                                 # Apply the admin_required decorator to this route
def admin_home():                               # Define the view function for admin home
    return redirect(url_for('admin.admin_dashboard'))   # Redirect to the admin dashboard route

# 📊 DASHBOARD
@admin_bp.route('/dashboard')                   # Register a route for '/admin/dashboard'
@admin_required                                 # Require admin privileges
def admin_dashboard():                          # Define the dashboard view function

    conn = get_db_connection()                  # Get a database connection
    cursor = conn.cursor(dictionary=True)       # Create a cursor that returns rows as dictionaries

    search = (request.args.get('search') or '').strip().lower()   # Get 'search' query parameter, default to empty string, strip and lowercase

    if search:                                  # If a search term is provided
        sql = """                               # SQL query to search students by name fields or sr_no
        SELECT * FROM students
        WHERE LOWER(first_name) LIKE %s
        OR LOWER(last_name) LIKE %s
        OR LOWER(father_name) LIKE %s
        OR sr_no = %s
        """

        sr_no_val = int(search) if search.isdigit() else -1   # Convert search to integer if it's all digits, else -1 (no match)

        cursor.execute(sql, (                   # Execute the SQL with parameters:
            search + '%',                       # For first_name prefix search
            search + '%',                       # For last_name prefix search
            search + '%',                       # For father_name prefix search
            sr_no_val                           # Exact match on sr_no (numeric)
        ))
    else:                                       # If no search term
        cursor.execute("SELECT * FROM students ORDER BY sr_no")   # Fetch all students ordered by serial number

    students = cursor.fetchall()                # Retrieve all rows from the executed query

    cursor.close()                              # Close the cursor
    conn.close()                                # Close the database connection

    return render_template('admin_dashboard.html', students=students, search=search)   # Render the dashboard template with students and search term

# ➕ ADD STUDENT
@admin_bp.route('/add', methods=['GET', 'POST'])   # Register route for '/admin/add' supporting GET and POST
@admin_required                                 # Require admin login
def admin_add():                                # Define the add student view function

    if request.method == 'POST':                # Handle form submission

        conn = get_db_connection()              # Get database connection
        cursor = conn.cursor()                  # Create a standard cursor (not dictionary)

        def safe_int(val): return int(val) if val and val.strip() else 0   # Helper to convert to int safely, default 0
        def safe_float(val): return float(val) if val and val.strip() else 0.0   # Helper to convert to float safely, default 0.0

        cursor.execute("SELECT MAX(sr_no) FROM students")   # Get the maximum existing sr_no
        new_id = (cursor.fetchone()[0] or 0) + 1            # Calculate new sr_no as max+1 (or 1 if table empty)

        data = (                                    # Prepare tuple of values for INSERT
            new_id,                                 # sr_no
            request.form.get('Last_Name') or '',    # last_name
            request.form.get('First_Name') or '',   # first_name
            request.form.get('Father_Name') or '',  # father_name
            request.form.get('Mother_Name') or '',  # mother_name
            request.form.get('DOB') or None,        # dob (date of birth)
            request.form.get('Category') or '',     # category
            request.form.get('SubCategory_Flag') or '',   # subcategory_flag
            request.form.get('Exam') or '',         # exam
            request.form.get('Seat_No') or '',      # seat_no
            safe_float(request.form.get('Percentage')),   # percentage
            request.form.get('Passing_Month_Year') or '', # passing_month_year
            safe_int(request.form.get('ID1')),      # id1
            safe_int(request.form.get('ID2')),      # id2
            safe_int(request.form.get('ID3')),      # id3
            safe_int(request.form.get('Score1')),   # score1
            safe_int(request.form.get('Score2')),   # score2
            safe_int(request.form.get('Score3')),   # score3
        )

        cursor.execute("""                        # Execute INSERT query with all fields
        INSERT INTO students VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)

        conn.commit()                             # Commit the transaction
        cursor.close()                            # Close cursor
        conn.close()                              # Close connection

        flash("Student added successfully!", "success")   # Flash success message
        return redirect(url_for('admin.admin_dashboard')) # Redirect to admin dashboard

    return render_template('admin_add.html')      # For GET request, display the add student form

# ✏️ EDIT STUDENT
@admin_bp.route('/edit/<int:sr_no>', methods=['GET', 'POST'])   # Route with URL parameter sr_no (integer), supports GET and POST
@admin_required                                 # Admin required
def admin_edit(sr_no):                          # Define edit function that receives sr_no

    conn = get_db_connection()                  # Get database connection
    cursor = conn.cursor(dictionary=True)       # Create dictionary cursor for fetching student data

    if request.method == 'POST':                # Handle form submission (update)

        def safe_int(val): return int(val) if val and val.strip() else 0   # Safe integer conversion
        def safe_float(val): return float(val) if val and val.strip() else 0.0   # Safe float conversion

        sql = """                               # UPDATE query template
        UPDATE students SET
            last_name=%s, first_name=%s, father_name=%s, mother_name=%s,
            dob=%s, category=%s, subcategory_flag=%s,
            exam=%s, seat_no=%s, percentage=%s,
            passing_month_year=%s, id1=%s, id2=%s, id3=%s,
            score1=%s, score2=%s, score3=%s
        WHERE sr_no=%s
        """

        values = (                              # Tuple of values for the update
            request.form.get('Last_Name') or '',    # last_name
            request.form.get('First_Name') or '',   # first_name
            request.form.get('Father_Name') or '',  # father_name
            request.form.get('Mother_Name') or '',  # mother_name
            request.form.get('DOB') or None,        # dob
            request.form.get('Category') or '',     # category
            request.form.get('SubCategory_Flag') or '',   # subcategory_flag
            request.form.get('Exam') or '',         # exam
            request.form.get('Seat_No') or '',      # seat_no
            safe_float(request.form.get('Percentage')),   # percentage
            request.form.get('Passing_Month_Year') or '', # passing_month_year
            safe_int(request.form.get('ID1')),      # id1
            safe_int(request.form.get('ID2')),      # id2
            safe_int(request.form.get('ID3')),      # id3
            safe_int(request.form.get('Score1')),   # score1
            safe_int(request.form.get('Score2')),   # score2
            safe_int(request.form.get('Score3')),   # score3
            sr_no                                   # WHERE condition parameter
        )

        cursor.execute(sql, values)             # Execute the UPDATE query
        conn.commit()                           # Commit changes

        cursor.close()                          # Close cursor
        conn.close()                            # Close connection

        flash("Student updated successfully!", "success")   # Flash success message
        return redirect(url_for('admin.admin_dashboard'))   # Redirect to dashboard

    cursor.execute("SELECT * FROM students WHERE sr_no=%s", (sr_no,))   # Fetch the student to edit
    student = cursor.fetchone()                 # Get the single row

    cursor.close()                              # Close cursor
    conn.close()                                # Close connection

    return render_template('admin_edit.html', student=student)   # Render edit form with student data

# ❌ DELETE
@admin_bp.route('/delete/<int:sr_no>')          # Route for delete (GET request, but should ideally be POST)
@admin_required                                 # Admin required
def admin_delete(sr_no):                        # Define delete function

    conn = get_db_connection()                  # Get database connection
    cursor = conn.cursor()                      # Create a cursor

    cursor.execute("DELETE FROM students WHERE sr_no=%s", (sr_no,))   # Execute DELETE query
    conn.commit()                               # Commit the deletion

    cursor.close()                              # Close cursor
    conn.close()                                # Close connection

    flash("Student deleted successfully!", "success")   # Flash success message
    return redirect(url_for('admin.admin_dashboard'))   # Redirect to dashboard

# 🚪 LOGOUT
@admin_bp.route('/logout')                      # Route for admin logout
def admin_logout():                             # Define logout view function
    session.clear()                             # Clear all session data
    flash("You have been logged out.", "info")  # Flash an info message
    return redirect(url_for('main.login'))      # Redirect to the login page (main blueprint)