from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import hashlib
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Immithun2605@'
app.config['MYSQL_DB'] = 'user_authentication'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

app.secret_key = 'your_secret_key'


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        profile_picture = request.files['profile_picture']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address_line1 = request.form['address_line1']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        user_type = request.form['user_type']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True) 

        profile_picture_path = os.path.join(uploads_dir, secure_filename(profile_picture.filename))
        profile_picture.save(profile_picture_path)

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (first_name, last_name, profile_picture, username, email, password, address_line1, city, state, pincode, user_type) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (first_name, last_name, profile_picture_path, username, email, hashed_password, address_line1, city, state, pincode, user_type)
        )
        mysql.connection.commit()
        cur.close()

        flash('Signup successful. Please log in.', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return render_template('dashboard.html', user=user)

    flash('Login required', 'error')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
