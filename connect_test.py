import psycopg2



DB_NAME = 'find_business_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

def get_db_connection(db_name=DB_NAME): #This a Function Define get_db_connection() that will establish and return a connection object to the PostgreSQL database: And again we pass in a default parameter in the function definition db_name = DB_NAME. NOTE: You don't need to assign  'dbname = DB_NAME' inside the function because db_name already holds the default value provided which is db_name.
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Successfully connected to database!")
        return conn
        """##Purpose of return conn:
        When psycopg2.connect() successfully establishes a connection to the PostgreSQL database, conn (the connection object)
        is returned immediately. This allows the calling code to receive the database connection object (conn) and proceed with 
        executing SQL queries or other operations on the database.##"""
        
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None
#         # This Return None is Optional, you can decide to return None or Leave it 

        

        
        
        
# ============================================================================
# Another Way Of Connecting To Database: You Can Uncomnent #
#=============================================================================

# def connect_To_Database():
#     try: 
#         connection = psycopg2.connect(
#             database = 'find_business_db', 
#             user = 'postgres',
#             password = 'postgres', 
#             host = 'localhost'
#             )
#         print("Connection Success")
#         return connection
    
#     except psycopg2.Error as e:
#         print(f"Connection Fail, Error: {e} ")
#     except Exception as e:
#         print(f"")
    
# connect_To_Database()

# def create_tables():
#     conn = connect_To_Database()
#     if conn:
#         try:
#             cur = conn.cursor()
            
#             # Create the 'users' table if it doesn't exist
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS users (
#                     id SERIAL PRIMARY KEY,
#                     first_name VARCHAR(50),
#                     last_name VARCHAR(50),
#                     email VARCHAR(100) UNIQUE,
#                     password VARCHAR(255)
#                 );
#             """)
#         except psycopg2.Error as e:
#             print(f"Database error: {e}")
#         except Exception as e:
#             print(f"Error: {e}")
#         finally:
#             cur.close()
#             conn.close()
#     else:
#         print("Could not open connection to the database")

# # Call the function to initialize the database
# create_tables()