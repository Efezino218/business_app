# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.errors import UniqueViolation
from werkzeug.security import generate_password_hash, check_password_hash
from connect import get_db_connection
from werkzeug.utils import secure_filename
import re, os
from functools import wraps
from datetime import date, datetime, timedelta
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./static/uploads" #we specify the path the image will be uploaded 
app.config['SECRET_KEY'] = "your_secret_key" #change the secrete key passoword when u are ablut to deploy the app, for stronger security
# app.secret_key = 'your_secret_key'

# Set up the configuration for flask_mail.
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
# //update it with your gmail
app.config['MAIL_USERNAME'] = 'efezinorich@gmail.com'
# //update it with your password
app.config['MAIL_PASSWORD'] = 'zcqw ngru qbea qsqm' #this is the password that google generate as we create New App on my login google account
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Create an instance of Mail.
mail = Mail(app)

# Define the route and send mail.
@app.route("/send_email")
def send_email():
  msg = Message('Hello from the other side!', sender = 'efezinorich@gmail.com', recipients = ['cyjustwebsolution@gmail.com'])
  msg.body = "hey, sending out email from flask!!!"
  msg.html = "<h1>Message Sent</h1>"
  mail.send(msg)
  return msg.html


# UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'wmv'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# UPLOAD Images and Videos Function
def upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return file_path
    return None
           
# Function to check if user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Creating the Admin hashed_password === we converted the pasword 'admin1234abcd and printed it as a hashed_pasword and inserted it to the database
password = 'admin1234abcd'
hashed_password = generate_password_hash(password)
print(hashed_password) #NOTE: The database do not allow plain text password, that is why we hashed the passowrd first in other to insert it


### ======Admin Users Business Control Routes======####
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, password FROM users WHERE email = %s AND is_admin = TRUE", (email,))
        admin = cur.fetchone()
        cur.close()
        conn.close()
        
        if admin and check_password_hash(admin[3], password):
            session['user_id'] = admin[0]
            session['first_name'] = admin[1]
            session['last_name'] = admin[2]
            session['is_admin'] = True
            flash('Admin login successful.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials or not an admin.', 'error')
    
    return render_template('admin_login.html')

# @app.route('/admin/dashboard')
# @login_required
# def admin_dashboard():
#     if not session.get('is_admin'):
#         flash('Access denied.', 'error')
#         return redirect(url_for('index'))
    
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id, shop_no, bus_name, description, user_id, subscription_active FROM businesses")
#     businesses = cur.fetchall()
#     cur.close()
#     conn.close()
    
#     return render_template('admin_view_business.html', businesses=businesses)


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))

    page = request.args.get('page', 'view_users')
    current_page = int(request.args.get('current_page', 1))
    items_per_page = 10
    offset = (current_page - 1) * items_per_page

    conn = get_db_connection()
    cur = conn.cursor()

    if page == 'view_users':
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]
        cur.execute("SELECT id, first_name, last_name, email, is_admin FROM users LIMIT %s OFFSET %s", (items_per_page, offset))
        users = cur.fetchall()
        total_pages = (total_users + items_per_page - 1) // items_per_page
        context = {'users': users, 'total_pages': total_pages, 'current_page': current_page}
    elif page == 'view_businesses':
        cur.execute("SELECT COUNT(*) FROM businesses")
        total_businesses = cur.fetchone()[0]
        cur.execute("SELECT id, shop_no, bus_name, description, user_id, subscription_active FROM businesses LIMIT %s OFFSET %s", (items_per_page, offset))
        businesses = cur.fetchall()
        total_pages = (total_businesses + items_per_page - 1) // items_per_page
        context = {'businesses': businesses, 'total_pages': total_pages, 'current_page': current_page}
    else:
        context = {}

    cur.close()
    conn.close()

    return render_template('admin_dashboard.html', page=page, **context)

# @app.route('/admin_dashboard')
# @login_required
# def admin_dashboard():
#     if not session.get('is_admin'):
#         flash('You do not have permission to access this page.', 'error')
#         return redirect(url_for('index'))

#     page = request.args.get('page', 'view_users')
    
#     conn = get_db_connection()
#     cur = conn.cursor()

#     if page == 'view_users':
#         cur.execute("SELECT id, first_name, last_name, email, is_admin FROM users")
#         users = cur.fetchall()
#         context = {'users': users}
#     elif page == 'view_businesses':
#         cur.execute("SELECT id, shop_no, bus_name, description, user_id, subscription_active FROM businesses")
#         businesses = cur.fetchall()
#         context = {'businesses': businesses}
#     elif page == 'update_business':
#         cur.execute("SELECT id, shop_no, bus_name, description, user_id, subscription_active FROM businesses")
#         businesses = cur.fetchall()
#         context = {'businesses': businesses}
#     else:
#         context = {}

#     cur.close()
#     conn.close()

#     return render_template('admin_dashboard.html', page=page, **context)



@app.route('/admin/business')
@login_required
def admin_business():
    if not session.get('is_admin'):
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, shop_no, bus_name, description, user_id, subscription_active FROM businesses")
    businesses = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin_view_business.html', businesses=businesses)


@app.route('/admin/delete_business/<int:business_id>', methods=['POST'])
@login_required
def admin_delete_business(business_id):
    if not session.get('is_admin'):
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Delete the subscriptions associated with the business
    cur.execute("DELETE FROM subscriptions WHERE business_id = %s", (business_id,))
    
    # Now delete the business
    cur.execute("DELETE FROM businesses WHERE id = %s", (business_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Business and associated subscriptions deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_update_business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def admin_update_business(business_id):
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        shop_no = request.form['shop_no']
        bus_name = request.form['bus_name']
        description = request.form['description']
        user_id = request.form['user_id']
        subscription_active = request.form.get('subscription_active') == 'on'

        cur.execute("""
            UPDATE businesses SET shop_no=%s, bus_name=%s, description=%s, user_id=%s, subscription_active=%s
            WHERE id=%s
        """, (shop_no, bus_name, description, user_id, subscription_active, business_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('Business updated successfully!', 'success')
        return redirect(url_for('admin_dashboard', page='view_businesses'))

    cur.execute("SELECT id, shop_no, bus_name, description, user_id, subscription_active FROM businesses WHERE id=%s", (business_id,))
    business = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('admin_update_business_form.html', business=business)

### ======Admin Users Business Control Routes  END======####


### ======Admin Control Users Control======####

@app.route('/admin/users')
@login_required
def admin_view_users():
    if not session.get('is_admin'):
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, email, is_admin FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin_view_users.html', users=users)

@app.route('/admin_update_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_update_user(user_id):
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        is_admin = request.form.get('is_admin') == 'on'

        cur.execute("""
            UPDATE users SET first_name=%s, last_name=%s, email=%s, is_admin=%s
            WHERE id=%s
        """, (first_name, last_name, email, is_admin, user_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard', page='view_users'))

    cur.execute("SELECT id, first_name, last_name, email, is_admin FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('admin_update_user_form.html', user=user)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Delete the user
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting user: {e}', 'error')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_view_users'))



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

## Forgotton password Route and Functions ##

def generate_reset_token(user_id):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return None
    return user_id

def send_reset_email(email, token):
    reset_url = url_for('reset_password', token=token, _external=True)
    msg = Message('Password Reset Request', sender='efezinorich@gmail.com', recipients=[email])
    msg.body = f'To reset your password, click the following link: {reset_url}'
    msg.html = f'<p>To reset your password, click the following link: <a href="{reset_url}">{reset_url}</a></p>'
    mail.send(msg)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            token = generate_reset_token(user[0])
            send_reset_email(email, token)
            flash('An email with a password reset link has been sent to your email address.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Email address not found.', 'error')

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = verify_reset_token(token)
    if not user_id:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, user_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')


@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT first_name, last_name, email, users_image FROM users WHERE id = %s', (user_id,))
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
        
            # Check if a new image file is uploaded
        if 'file' in request.files and request.files['file'].filename != "":
            file_path = upload_file(request.files['file'])
            # print(file_path)
            
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        cur.execute('UPDATE users SET first_name = %s, last_name = %s, email = %s, users_image = %s, password = %s  WHERE id = %s',
                    (new_fname, new_lname, new_email, file_path, hashed_password, user_id))

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
        
        # Redirect to the search results page with the search term as a query parameter
        return redirect(url_for('search_business_result', search_term=search_term))
    
    return render_template('search_business.html')

@app.route('/search_business_result')
@login_required
def search_business_result():
    search_term = request.args.get('search_term', '').strip() #The empty string in request.args.get('search_term', '') serves as a default value in case the search_term query parameter is not provided in the URL, that is if a user submit an empty search
    
    if not search_term:
        flash('No search term provided.', 'error')
        return redirect(url_for('search_business'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Use ILIKE for case-insensitive search and wildcard for partial matches
    cur.execute('SELECT * FROM businesses WHERE shop_no ILIKE %s OR bus_name ILIKE %s', (f'%{search_term}%', f'%{search_term}%'))
    business = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if not business:
        flash('No businesses found. You can add a new business.', 'error')
        return redirect(url_for('business_not_found'))
    
    return render_template('search_business_result.html', business=business, search_term=search_term)

@app.route('/business_not_found')
@login_required
def business_not_found():
    return render_template('business_not_found.html')

@app.route('/add_business', methods=['GET', 'POST'])
@login_required
def add_business():
    if request.method == 'POST':
        
        shop_no = request.form['shop_no']
        bus_name = request.form['bus_name']
        description = request.form['description']
        
        # Check if a new image file is uploaded
        if 'file' in request.files and request.files['file'].filename != "":
            file_path = upload_file(request.files['file'])
        
        # Check if a new video file is uploaded
        if 'video' in request.files and request.files['video'].filename != "":
            video_path = upload_file(request.files['video'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('INSERT INTO businesses (shop_no, image_url, video_url, bus_name, description, user_id) VALUES (%s, %s, %s, %s, %s, %s)',
                    (shop_no, file_path, video_path, bus_name, description, session['user_id']))
        conn.commit()
        # cur.execute('UPDATE businesses SET shop_no = %s, bus_name = %s, description = %s, image_url = %s, video_url = %s WHERE id = %s',
        #             (shop_no, bus_name, description, file_path, video_path, business_id))
        
        cur.close()
        conn.close()
        
        flash('Business added successfully.', 'success')
        return redirect(url_for('business'))

    return render_template('add_business.html')
    

@app.route('/update_business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def update_business(business_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM businesses WHERE id = %s', (business_id,))
    business = cur.fetchone()
    
    if not business:
        flash('Business not found.', 'error')
        return redirect(url_for('business'))
    
    if request.method == 'POST':
        shop_no = request.form['shop_no']
        bus_name = request.form['bus_name']
        description = request.form['description']
        
        file_path = business[6]  # Assuming the image URL is in the 5th column (index 4)
        video_path = business[4]  # Assuming the video URL is in the 6th column (index 5)

        # Check if a new image file is uploaded
        if 'file' in request.files and request.files['file'].filename != "":
            file_path = upload_file(request.files['file'])
        
        # Check if a new video file is uploaded
        if 'video' in request.files and request.files['video'].filename != "":
            video_path = upload_file(request.files['video'])
        
        cur.execute('UPDATE businesses SET shop_no = %s, bus_name = %s, description = %s, image_url = %s, video_url = %s WHERE id = %s',
                    (shop_no, bus_name, description, file_path, video_path, business_id))
        
        conn.commit()
        
        flash('Business updated successfully.', 'success')
        return redirect(url_for('view_business', business_id=business_id))

    return render_template('update_business.html', business=business)


@app.route('/view_business/<int:business_id>')
def view_business(business_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT shop_no, bus_name, description, image_url FROM businesses WHERE id = %s", (business_id,))
    # cur.execute("SELECT id, shop_no, bus_name, description, user_id, image_url FROM businesses", (business_id,))
    business = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('view_business.html', business=business)


@app.route('/business')
def business():
      # Fetch the logged-in user ID from session
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, shop_no, bus_name, description, user_id, image_url, video_url FROM businesses")
    businesses = cur.fetchall()
    print(businesses)
    cur.close()
    conn.close()
    return render_template('businesses.html', businesses=businesses, user_id = session.get('user_id') )

@app.route('/my_businesses')
@login_required
def my_businesses():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, shop_no, bus_name, description,  image_url, video_url FROM businesses WHERE user_id = %s", (user_id,))
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

    
# Advertisement Routes
from datetime import timedelta  # Make sure to import timedelta
# Function to handle the subscription payment
def create_subscription(user_id, business_id, subscription_type):
    start_date = datetime.now().date()
    if subscription_type == 'monthly':
        end_date = start_date + timedelta(days=30)
    elif subscription_type == 'yearly':
        end_date = start_date + timedelta(days=365)
    amount_paid = 50.0
    status = 'active'

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO subscriptions (user_id, business_id, subscription_type, start_date, end_date, status, amount_paid) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (user_id, business_id, subscription_type, start_date, end_date, status, amount_paid))
    cur.execute('UPDATE businesses SET subscription_active = TRUE WHERE id = %s', (business_id,))
    conn.commit()
    cur.close()
    conn.close()



# #========SuBscribe Route That Handle Payment======#
@app.route('/subscribe/<int:business_id>', methods=['GET', 'POST'])
@login_required
def subscribe(business_id):
    user_id = session['user_id']
    
    # Check if the user is the owner of the business
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM businesses WHERE id = %s", (business_id,))
    business_owner = cur.fetchone()
    
    if not business_owner or business_owner[0] != user_id:
        flash('You can only subscribe for your own business.', 'error')
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        subscription_type = request.form['subscription_type']
        card_number = request.form['card_number']
        card_expiry = request.form['card_expiry']
        card_cvv = request.form['card_cvv']
        amount_paid = 50.00 if subscription_type == 'monthly' else 500.00

        # Extract MM/YY from the card_expiry field (which will be in the format YYYY-MM)

        try:
            # Format card_expiry to MM/YY
            # Split and format card expiry MM/YY
            card_expiry_parts = card_expiry.split('/')
            if len(card_expiry_parts) != 2:
                raise ValueError("Invalid card_expiry format")

            month = card_expiry_parts[0].strip()
            year = card_expiry_parts[1].strip()

            # Validate month and year are valid numbers
            if not (month.isdigit() and year.isdigit()):
                raise ValueError("Invalid card_expiry format")

            # Format the card_expiry in 'MM/YY' format
            card_expiry_formatted = f"{month}/{year}"
        except ValueError as e:
            flash(f'Invalid card expiry format: {e}', 'error')
            cur.close()
            conn.close()
            return redirect(url_for('subscribe', business_id=business_id))        
        
        # Insert payment information into the payments table
        cur.execute("""
            INSERT INTO payments (user_id, business_id, subscription_type, card_number, card_expiry, card_cvv, amount_paid)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, business_id, subscription_type, card_number, card_expiry_formatted, card_cvv, amount_paid))

        # Create a new subscription
        cur.execute("""
            INSERT INTO subscriptions (user_id, business_id, subscription_type, start_date, end_date, status, amount_paid)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '1 month' * %s, 'active', %s)
        """, (user_id, business_id, subscription_type, 1 if subscription_type == 'monthly' else 12, amount_paid))

        conn.commit()
        cur.close()
        conn.close()

        flash('Subscription successful.', 'success')
        return redirect(url_for('index'))
    
    return render_template('subscribe.html', business_id=business_id)

  
  
  
    
# #========SuBscribe Route That Do Not Handle Payment======#
# @app.route('/subscribe/<int:business_id>', methods=['GET', 'POST'])
# @login_required
# def subscribe(business_id):
#     user_id = session['user_id']
    
#     # Check if the user is the owner of the business
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT user_id FROM businesses WHERE id = %s", (business_id,))
#     business_owner = cur.fetchone()
    
#     if not business_owner or business_owner[0] != user_id:
#         flash('You can only subscribe for your own business.', 'error')
#         cur.close()
#         conn.close()
#         return redirect(url_for('index'))
    
#     if request.method == 'POST':
#         subscription_type = request.form['subscription_type']
        
#         # Check if the user already has an active subscription for the same business
#         cur.execute("""
#             SELECT * FROM subscriptions 
#             WHERE user_id = %s AND business_id = %s AND status = 'active'
#         """, (user_id, business_id))
#         existing_subscription = cur.fetchone()
        
#         if existing_subscription:
#             flash('You already have an active subscription for this business.', 'error')
#             cur.close()
#             conn.close()
#             return redirect(url_for('subscribe', business_id=business_id))
        
#         # Handle payment process (skipped here for simplicity)
        
#         # Create the subscription
#         create_subscription(user_id, business_id, subscription_type)
#         flash('Subscription successful.', 'success')
#         cur.close()
#         conn.close()
#         return redirect(url_for('index'))
    
#     cur.close()
#     conn.close()
#     return render_template('subscribe.html', business_id=business_id)


#========Unsubscribe Route======#
@app.route('/unsubscribe/<int:business_id>', methods=['POST'])
@login_required
def unsubscribe(business_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if the user is the owner of the business
    cur.execute("SELECT user_id FROM businesses WHERE id = %s", (business_id,))
    business_owner = cur.fetchone()
    
    if not business_owner or business_owner[0] != user_id:
        flash('You can only unsubscribe your own business.', 'error')
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    
    # Check if the user has an active subscription for the business
    cur.execute("""
        SELECT id FROM subscriptions 
        WHERE user_id = %s AND business_id = %s AND status = 'active'
    """, (user_id, business_id))
    active_subscription = cur.fetchone()
    
    if active_subscription:
        cur.execute("""
            UPDATE subscriptions 
            SET status = 'inactive'
            WHERE id = %s
        """, (active_subscription[0],))
        conn.commit()
        flash('Unsubscribed successfully.', 'success')
    else:
        flash('No active subscription found for this business.', 'error')
    
    cur.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/my_subscriptions')
@login_required
def my_subscriptions():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT s.id, b.bus_name, s.subscription_type, s.start_date, s.end_date, s.status, s.amount_paid
        FROM subscriptions s
        JOIN businesses b ON s.business_id = b.id
        WHERE s.user_id = %s AND s.status = 'active'
    ''', (user_id,)) 
    
    """UNDERSTAND How the querry is being made from the database below:
    s.id: The id column from the subscriptions table.
    b.bus_name: The bus_name column from the businesses table.
    s.subscription_type, s.start_date, s.end_date, s.status, s.amount_paid: Columns from the subscriptions table.
    NOTE: s is an alias for the subscriptions table. Example: s.id refers to the id column in the subscriptions table. 
            b is an alias for the businesses table. Example: b.bus_name refers to the bus_name column in the businesses table.

    """    
    subscriptions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('my_subscriptions.html', subscriptions=subscriptions)


@app.route('/')
def index():
    user_id = session.get('user_id')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of businesses per page

    conn = get_db_connection()
    cur = conn.cursor()

    # Get total count of businesses for pagination
    cur.execute("SELECT COUNT(*) FROM businesses")
    total_count = cur.fetchone()[0]
    total_pages = (total_count + per_page - 1) // per_page

    # Get paginated businesses with subscription info
    cur.execute("""
        SELECT b.id, b.shop_no, b.bus_name, b.description, b.user_id, b.image_url,
               (SELECT COUNT(*) FROM subscriptions s WHERE s.business_id = b.id AND s.status = 'active') AS subscription_active
        FROM businesses b
        ORDER BY subscription_active DESC, b.id
        LIMIT %s OFFSET %s
    """, (per_page, (page - 1) * per_page))
    businesses = cur.fetchall()

    users_image = None  
    if user_id:
        cur.execute("SELECT users_image, id FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            users_image = user_data[0]
            print(users_image)
    
    cur.close()
    conn.close()
    
    context = {
        "user_id": user_id, 
        "first_name": first_name, 
        "last_name": last_name, 
        "businesses":businesses, 
        "page":page, 
        "total_pages":total_pages,
        "users_image": users_image
    }
    return render_template('index.html', **context)



# @app.route('/')
# def index():
#     user_id = session.get('user_id')
#     first_name = session.get('first_name')
#     last_name = session.get('last_name')
    
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id, shop_no, bus_name, description, user_id FROM businesses")
#     businesses = cur.fetchall()
#     cur.close()
#     conn.close()
    
#     return render_template('index.html', user_id=user_id, first_name=first_name, last_name=last_name, businesses=businesses)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
