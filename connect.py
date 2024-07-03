import psycopg2


def get_db_connection():
    try:
        conn = psycopg2.connect(host='localhost', database='find_business_db', user='postgres', password='postgres')
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
            
            print("Database tables created successfully")
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