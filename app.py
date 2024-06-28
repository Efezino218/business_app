# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.errors import UniqueViolation
from werkzeug.security import generate_password_hash, check_password_hash
from connect import get_db_connection
from werkzeug.utils import secure_filename
import re, os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS_IMAGES = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_VIDEOS = {'mp4', 'mov', 'avi', 'wmv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Function to check if user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to check if email is valid using regular expressions
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        # Validate email format
        if not is_valid_email(email):
            flash('Invalid email format. Please enter a valid email.', 'error')
            return render_template('register.html')

        # Validate password complexity
        if len(password) < 6 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            flash('Password must be at least 6 characters long and contain both numbers and alphabets.', 'error')
            return render_template('register.html')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)',
                        (first_name, last_name, email, generate_password_hash(password, method='pbkdf2:sha256')))
            conn.commit()
        except UniqueViolation:
            conn.rollback()
            flash('Email already exists. Please use a different email.', 'error')
            return render_template('register.html')
        finally:
            cur.close()
            conn.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[4], password):
            session['user_id'] = user[0]
            session['first_name'] = user[1]
            session['last_name'] = user[2]
            print(f"Session set: {session['first_name']} {session['last_name']}")
            return redirect(url_for('index'))

        flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT first_name, last_name, email FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('profile.html', user=user)



@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user_id = session['user_id']     
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        new_fname = request.form.get("first_name")
        new_lname = request.form.get("last_name")
        new_email = request.form.get("email")
        new_password = request.form.get("password")

        # Check if email is valid
        if not is_valid_email(new_email):
            flash('Invalid email address. Please enter a valid email.', 'error')
            return redirect(url_for('edit_profile'))

        # Check if password meets criteria
        if len(new_password) < 6 or not re.search("[a-zA-Z]", new_password) or not re.search("[0-9]", new_password):
            flash('Password must be at least 6 characters long and contain both letters and numbers.', 'error')
            return redirect(url_for('edit_profile'))

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        cur.execute('UPDATE users SET first_name = %s, last_name = %s, email = %s, password = %s WHERE id = %s',
                    (new_fname, new_lname, new_email, hashed_password, user_id))

        conn.commit()
        cur.close()
        conn.close()

        session['first_name'] = new_fname
        session['last_name'] = new_lname
        
        flash(f"User profile updated successfully", 'success')     
        return redirect(url_for('index'))
    
    cur.execute('SELECT first_name, last_name, email FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_profile.html', user=user)


# BUSINESS PROFILE
@app.route('/search_business', methods=['GET', 'POST'])
@login_required
def search_business():
    if request.method == 'POST':
        search_term = request.form['search_term'].strip()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if a business with the given shop number or name exists
        cur.execute('SELECT * FROM businesses WHERE shop_no ILIKE %s OR bus_name ILIKE %s', (f'%{search_term}%', f'%{search_term}%'))
        business = cur.fetchone() # in this situation cur.fetchone will only fetch one single data that a user search for inside the colum shop_no, that is ther reason we we cur.fetch one
        
        cur.close()
        conn.close()
        
        if business:
            # If business found, redirect to update page
            return redirect(url_for('update_business', business_id=business[0]))
        else:
            # If business not found, redirect to add new business page
            flash('Business not found. You can add a new business.', 'error')
            return redirect(url_for('add_business'))

    return render_template('search_business.html')

# @app.route('/add_business', methods=['GET', 'POST'])
# @login_required
# def add_business():
#     if request.method == 'POST':
#         shop_no = request.form['shop_no']
#         bus_name = request.form['bus_name']
#         description = request.form['description']
        
#         # Handle image upload
#         if 'image_file' in request.files:
#             image_file = request.files['image_file']
#             if image_file.filename != '' and allowed_file(image_file.filename, ALLOWED_EXTENSIONS_IMAGES):
#                 filename = secure_filename(image_file.filename)
#                 image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 image_file.save(image_url)
#             else:
#                 flash('Invalid image file format. Allowed formats are: png, jpg, jpeg, gif', 'error')
#                 return redirect(request.url)

#         # Handle video upload
#         if 'video_file' in request.files:
#             video_file = request.files['video_file']
#             if video_file.filename != '' and allowed_file(video_file.filename, ALLOWED_EXTENSIONS_VIDEOS):
#                 filename = secure_filename(video_file.filename)
#                 video_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 video_file.save(video_url)
#             else:
#                 flash('Invalid video file format. Allowed formats are: mp4, mov, avi, wmv', 'error')
#                 return redirect(request.url)

#         # Insert business into database
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute('INSERT INTO businesses (shop_no, bus_name, description, user_id, image_url, video_url) VALUES (%s, %s, %s, %s, %s, %s)',
#                     (shop_no, bus_name, description, session['user_id'], image_url, video_url))
#         conn.commit()
        
#         cur.close()
#         conn.close()
        
#         flash('Business added successfully.', 'success')
#         return redirect(url_for('business'))

#     return render_template('add_business.html')

@app.route('/add_business', methods=['GET', 'POST'])
@login_required
def add_business():
    if request.method == 'POST':
        shop_no = request.form['shop_no']
        bus_name = request.form['bus_name']
        description = request.form['description']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('INSERT INTO businesses (shop_no, bus_name, description, user_id) VALUES (%s, %s, %s, %s)',
                    (shop_no, bus_name, description, session['user_id']))
        conn.commit()
        
        cur.close()
        conn.close()
        
        flash('Business added successfully.', 'success')
        return redirect(url_for('business'))

    return render_template('add_business.html')


# UPLOAD Image Route: This is just a testing Route For Uploade
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            cur.execute('INSERT INTO businesses (image_url) VALUES (%s)', (image_url,))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('index'))
    return render_template('upload_files.html')

    
@app.route('/show_file/<int:business_id>', methods=['GET', 'POST'])
def show_file(business_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image_url FROM businesses WHERE id = %s", (business_id,))
    fetch_image = cur.fetchone()
    cur.close()
    conn.close()
    if fetch_image:
        fetch_image = fetch_image[0]
    return render_template('upload_files.html', fetch_image=fetch_image)

    

@app.route('/update_business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def update_business(business_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM businesses WHERE id = %s', (business_id,))
    business = cur.fetchone()
    
    if request.method == 'POST':
        shop_no = request.form['shop_no']
        bus_name = request.form['bus_name']
        description = request.form['description']
        
        cur.execute('UPDATE businesses SET shop_no = %s, bus_name = %s, description = %s WHERE id = %s',
                    (shop_no, bus_name, description, business_id))
        conn.commit()
        
        flash('Business updated successfully.', 'success')
        return redirect(url_for('search_business'))

    return render_template('update_business.html', business=business)

@app.route('/view_business/<int:business_id>')
def view_business(business_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT shop_no, bus_name, description FROM businesses WHERE id = %s", (business_id,))
    business = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('view_business.html', business=business)


@app.route('/business')
def business():
      # Fetch the logged-in user ID from session
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, shop_no, bus_name, description, user_id FROM businesses")
    businesses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('businesses.html', businesses=businesses, user_id = session.get('user_id') )

@app.route('/my_businesses')
@login_required
def my_businesses():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, shop_no, bus_name, description FROM businesses WHERE user_id = %s", (user_id,))
    businesses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('my_businesses.html', businesses=businesses)

@app.route('/delete_business/<int:business_id>', methods=['POST'])
@login_required
def delete_business(business_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM businesses WHERE id = %s AND user_id = %s", (business_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
    flash('Business successfully deleted', 'success')
    return redirect(url_for('business'))

    

@app.route('/')
def index():
    user_id = session.get('user_id')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, shop_no, bus_name, description, user_id FROM businesses")
    businesses = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', user_id=user_id, first_name=first_name, last_name=last_name, businesses=businesses)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
