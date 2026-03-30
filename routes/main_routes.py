from flask import Blueprint, render_template, request, redirect, url_for, session   # Import Flask components for blueprint, rendering, request handling, redirects, URL building, and session management
from werkzeug.security import check_password_hash   # Import password hashing verification function
from models.student import search_students          # Import the search function from student model
from models.db import get_db_connection             # Import database connection helper

main_bp = Blueprint('main', __name__)               # Create a Blueprint named 'main' with no URL prefix (default root)

# 🔐 PROTECT ONLY MAIN ROUTES (NOT ADMIN)
@main_bp.before_request                             # Decorator to run this function before every request to the main blueprint
def protect_routes():                               # Define the function that enforces login protection

    if not request.endpoint:                        # If there's no endpoint (e.g., 404), skip protection
        return

    # allow static files
    if request.endpoint.startswith('static'):       # If the request is for a static file (CSS, JS, etc.), allow access
        return

    # allow login page
    if request.endpoint == 'main.login':            # If the request is to the login page, allow access
        return

    # 🔒 protect only main routes
    if request.endpoint.startswith('main.'):        # If the request is for any other main blueprint route
        if not session.get('logged_in'):            # Check if the user is not logged in
            return redirect(url_for('main.login'))  # Redirect to the login page

# 🔑 LOGIN (TEACHER + ADMIN)
@main_bp.route('/login', methods=['GET', 'POST'])   # Register route for '/login' supporting both GET and POST
def login():                                        # Define the login view function

    if request.method == 'POST':                    # Handle form submission (POST)
        username = request.form.get('username')     # Retrieve username from form data
        password = request.form.get('password')     # Retrieve password from form data

        conn = get_db_connection()                  # Get database connection
        cursor = conn.cursor(dictionary=True)       # Create cursor that returns rows as dictionaries

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))   # Query user by username
        user = cursor.fetchone()                    # Fetch the user record (or None)

        cursor.close()                              # Close the cursor
        conn.close()                                # Close the database connection

        if user and check_password_hash(user['password_hash'], password):   # If user exists and password matches hash

            session.clear()                         # Clear any existing session data
            session['logged_in'] = True             # Mark user as logged in
            session['role'] = user['role']          # Store user's role (teacher or admin)
            session.permanent = True                # Make the session permanent (uses PERMANENT_SESSION_LIFETIME)

            # 🔀 redirect based on role
            if user['role'] == "admin":             # If role is admin
                return redirect(url_for('admin.admin_dashboard'))   # Redirect to admin dashboard
            else:                                   # Otherwise (teacher)
                return redirect(url_for('main.index'))   # Redirect to teacher dashboard

        return render_template('login.html', error="Invalid credentials")   # Show login page with error message

    return render_template('login.html')            # For GET request, display login page

# 🚪 LOGOUT
@main_bp.route('/logout')                           # Register route for '/logout'
def logout():                                       # Define logout view function
    session.clear()                                 # Clear all session data
    return redirect(url_for('main.login'))          # Redirect to login page

# 📊 TEACHER DASHBOARD (now passes role to template)
@main_bp.route('/')                                 # Register the root route (teacher dashboard)
def index():                                        # Define the index/dashboard view

    role = session.get('role')                      # Get the user's role from session

    # not logged
    if not role:                                    # If no role in session (i.e., not logged in)
        return redirect(url_for('main.login'))      # Redirect to login page

    # teacher allowed
    if role == "teacher":                           # If user is a teacher
        query = request.args.get('search', '')      # Get the search query from URL parameter (default empty string)
        students = search_students(query) if query else []   # If query provided, search; else empty list
        # ✅ Pass role to template so we can conditionally show admin button
        return render_template('index.html', students=students, query=query, role=role)   # Render teacher dashboard

    # admin trying to access → redirect
    if role == "admin":                             # If user is admin (shouldn't see teacher dashboard)
        return redirect(url_for('admin.admin_dashboard'))   # Redirect to admin dashboard

    # fallback
    session.clear()                                 # For any other unexpected role, clear session
    return redirect(url_for('main.login'))          # Redirect to login