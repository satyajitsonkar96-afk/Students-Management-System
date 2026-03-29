from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from models.student import search_students
from models.db import get_db_connection

main_bp = Blueprint('main', __name__)


# 🔐 PROTECT ONLY MAIN ROUTES (NOT ADMIN)
@main_bp.before_request
def protect_routes():

    if not request.endpoint:
        return

    # allow static files
    if request.endpoint.startswith('static'):
        return

    # allow login page
    if request.endpoint == 'main.login':
        return

    # 🔒 protect only main routes
    if request.endpoint.startswith('main.'):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))


# 🔑 LOGIN (TEACHER + ADMIN)
@main_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):

            session.clear()
            session['logged_in'] = True
            session['role'] = user['role']
            session.permanent = True

            # 🔀 redirect based on role
            if user['role'] == "admin":
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('main.index'))

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


# 🚪 LOGOUT
@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# 📊 TEACHER DASHBOARD (now passes role to template)
@main_bp.route('/')
def index():

    role = session.get('role')

    # not logged
    if not role:
        return redirect(url_for('main.login'))

    # teacher allowed
    if role == "teacher":
        query = request.args.get('search', '')
        students = search_students(query) if query else []
        # ✅ Pass role to template so we can conditionally show admin button
        return render_template('index.html', students=students, query=query, role=role)

    # admin trying to access → redirect
    if role == "admin":
        return redirect(url_for('admin.admin_dashboard'))

    # fallback
    session.clear()
    return redirect(url_for('main.login'))
