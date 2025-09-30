from flask import render_template, request, redirect, url_for, session, flash
from app import create_app
import mysql.connector
import os
app = create_app()
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['DB_CONFIG'] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'VK181920'),
    'database': os.getenv('DB_NAME', 'schemes_db')
}

@app.route('/')
def index():
    db = mysql.connector.connect(**app.config['DB_CONFIG'])
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM schemes")
    schemes = cursor.fetchall()
    db.close()
    return render_template('index.html', schemes=schemes)

@app.route('/scheme/<int:scheme_id>')
def scheme_detail(scheme_id):
    db = mysql.connector.connect(**app.config['DB_CONFIG'])
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM schemes WHERE id = %s", (scheme_id,))
    scheme = cursor.fetchone()
    db.close()
    if not scheme:
        return "Scheme not found", 404
    return render_template('scheme_detail.html', scheme=scheme)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = mysql.connector.connect(**app.config['DB_CONFIG'])
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        eligibility = request.form['eligibility']
        benefits = request.form['benefits']
        application_link = request.form['application_link']
        cursor.execute("""
            INSERT INTO schemes (name, category, eligibility, benefits, application_link)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, category, eligibility, benefits, application_link))
        db.commit()
        flash('Scheme added successfully!', 'success')

    query = request.args.get('query', '')
    if query:
        cursor.execute("SELECT * FROM schemes WHERE name LIKE %s OR category LIKE %s", (f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("SELECT * FROM schemes")

    schemes = cursor.fetchall()
    db.close()

    page = int(request.args.get('page', 1))
    per_page = 5
    start = (page - 1) * per_page
    schemes = schemes[start:start + per_page]

    return render_template('admin.html', schemes=schemes, query=query, page=page)

@app.route('/edit/<int:scheme_id>', methods=['GET', 'POST'])
def edit_scheme(scheme_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = mysql.connector.connect(**app.config['DB_CONFIG'])
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        eligibility = request.form['eligibility']
        benefits = request.form['benefits']
        application_link = request.form['application_link']
        cursor.execute("""
            UPDATE schemes SET name=%s, category=%s, eligibility=%s, benefits=%s, application_link=%s
            WHERE id=%s
        """, (name, category, eligibility, benefits, application_link, scheme_id))
        db.commit()
        db.close()
        flash('Scheme updated successfully!', 'info')
        return redirect(url_for('admin'))

    cursor.execute("SELECT * FROM schemes WHERE id = %s", (scheme_id,))
    scheme = cursor.fetchone()
    db.close()
    return render_template('edit.html', scheme=scheme)

@app.route('/delete/<int:scheme_id>')
def delete_scheme(scheme_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = mysql.connector.connect(**app.config['DB_CONFIG'])
    cursor = db.cursor()
    cursor.execute("DELETE FROM schemes WHERE id = %s", (scheme_id,))
    db.commit()
    db.close()
    flash('Scheme deleted successfully!', 'warning')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'viswa' and password == '23331A4715':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'danger')
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))