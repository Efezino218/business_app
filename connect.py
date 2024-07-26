import psycopg2


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            database='find_business_db', 
            user='postgres', 
            password='postgres'
            )
        print("Successfully connected to database!")
        return conn
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None


def create_tables():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Create the 'users' table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(255)
                );
            """)
            cur.execute("""
                ALTER TABLE users ADD COLUMN users_image VARCHAR(255);
            """)

            cur.execute("""
                ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;            
            """) # we added a user as an admin in other to have control to all users, that is why we Alter the table
            cur.execute("""
                INSERT INTO users (first_name, last_name, email, password, is_admin)
                VALUES ('Admin', 'User', 'admin@efe.com', 'scrypt:32768:8:1$FhsY54u44rREf2uQ$d11789089bfdabd5c9c70c6f429f77383fb48761e6010fe2fa482f6e9df6e532da971fe5334c2d9c8315d8dc29dbe03735918fcc72cd3889c10fbd913ecb6b83', TRUE);
            """) # after we alter the user table to add an admin control, we then insert the admin credentails, the detail of the admin
            #the place of the password, we first harshed the password the main app.py script that is how we are able to get that password 
            #  because the database do not allow plain text password, Go to app.py script to read the comment how we hashed the password
            
            
            # Create the 'businesses' table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    id SERIAL PRIMARY KEY,
                    shop_no VARCHAR(20) NOT NULL,
                    bus_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    video_url VARCHAR(255),
                    user_id INTEGER REFERENCES users(id),
                    image_url VARCHAR(255),
                    subscription_active BOOLEAN NOT NULL
                );
            """)
            
            # Create the 'subscriptions' table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    business_id INTEGER REFERENCES businesses(id),
                    start_date DATE,
                    end_date DATE,
                    status VARCHAR(10),
                    amount_paid NUMERIC
                );
            """)
            
            cur.execute("""
                ALTER TABLE subscriptions ALTER COLUMN status SET DEFAULT 'inactive';            
                """) # i created another routh for unsubscribe then i alter the 'status' column on the subscribtion table to be inactive 
            
            # Create the 'subscriptions' table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    business_id INTEGER REFERENCES businesses(id),
                    subscription_type VARCHAR(50),
                    card_number VARCHAR(19),
                    card_expiry VARCHAR(7),
                    card_cvv VARCHAR(3),
                    amount_paid DECIMAL(10, 2),
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
    
            
            print("Database tables created successfully")
            print("Column 'users_image' added successfully.")
            conn.commit()
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        print("Could not open connection to the database")

# Call the function to initialize the database
create_tables()




"""CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,
    subscription_type VARCHAR(10) NOT NULL,
    card_number VARCHAR(16) NOT NULL,
    expiration_date VARCHAR(5) NOT NULL,
    cvv VARCHAR(3) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payment_details (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,
    card_number VARCHAR(20) NOT NULL,
    card_expiry VARCHAR(5) NOT NULL,
    card_cvc VARCHAR(3) NOT NULL,
    payment_type VARCHAR(10) NOT NULL,  -- 'monthly' or 'yearly'
    amount NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    business_id INTEGER REFERENCES businesses(id),
    subscription_type VARCHAR(50),
    card_number VARCHAR(16),
    card_expiry VARCHAR(5),
    card_cvv VARCHAR(3),
    amount_paid DECIMAL(10, 2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""


# OR ANOTHER WAY OF CONNECTING TO DATABASE BELOW, BUT IS NOT MARJOLY REQUIRED
# def get_db_connection():
#     try:
#         conn = psycopg2.connect(host='localhost', database='find_business_db', user='postgres', password='postgres')
        
#         if conn:
#             cur = conn.cursor()
            
#             # -- Create the 'users' table if it doesn't exist
#             cur.execute(
#                 """
#                 CREATE TABLE IF NOT EXISTS users (
#                 id SERIAL PRIMARY KEY,
#                 first_name VARCHAR(50),
#                 last_name VARCHAR(50),
#                 email VARCHAR(100) UNIQUE,
#                 password VARCHAR(255)
#                 );
#                 """)

            
#             # -- Create the 'Businesses' table if it doesn't exist
#             cur.execute(
#                 """
#                 CREATE TABLE IF NOT EXISTS businesses (
#                 id SERIAL PRIMARY KEY,
#                 shop_no VARCHAR(20) NOT NULL,
#                 bus_name VARCHAR(100) NOT NULL,
#                 description TEXT,
#                 video_url VARCHAR(255),
#                 user_id INTEGER REFERENCES users(id),
#                 image_url VARCHAR(255),
#                 subscription_active BOOLEAN NOT NULL
#                 );
#                 """)
            
#             # -- Create the 'subscriptions' table if it doesn't exist
#             cur.execute( 
#                 """
#                 CREATE TABLE IF NOT EXISTS subscriptions (
#                 id SERIAL PRIMARY KEY,
#                 user_id INTEGER REFERENCES users(id),
#                 business_id INTEGER REFERENCES businesses(id),
#                 start_date DATE,
#                 end_date DATE,
#                 status VARCHAR(10),
#                 amount_paid NUMERIC
#             );
#             """)
#             print("Database Open and Table Created Successfully")
#             conn.commit()
        
#         else:
#             print("Could not Open Connection to database")       

#     except psycopg2.Error as e:
#         print(f"Database error: {e}")

#     except Exception as e:
#         print(f"Error: {e}")
        
#     return conn
            
# # Call the function
# get_db_connection()