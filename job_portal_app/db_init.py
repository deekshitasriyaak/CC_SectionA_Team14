import pymysql
import os
import sys

# MySQL connection configuration
db_config = {
    'host': os.getenv("JOB_DB_HOST", "job_db"),
    'user': os.getenv("JOB_DB_USER", "root"),
    'password': os.getenv("JOB_DB_PASSWORD", "chandu@123S"),
    'db': os.getenv("JOB_DB_NAME", "job_portal"),
}

def initialize_database():
    try:
        # First connect without specifying the database to ensure it exists
        print("Connecting to MySQL server...")
        conn = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        with conn.cursor() as cursor:
            # Create database if it doesn't exist
            print(f"Creating database {db_config['db']} if it doesn't exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['db']}")
        conn.close()
        
        # Now connect to the specific database
        print(f"Connecting to database {db_config['db']}...")
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['db'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Open a cursor to perform database operations
        with connection.cursor() as cursor:
            # Read the SQL script to create the tables
            print("Running database schema script...")
            try:
                with open('db_schema.sql', 'r') as file:
                    sql_script = file.read()
                
                # Execute each statement in the SQL script
                statements = sql_script.split(';')
                for statement in statements:
                    if statement.strip():
                        cursor.execute(statement)
                connection.commit()
                print("Database schema created successfully!")
            except Exception as e:
                print(f"Error executing SQL script: {e}")
                return False
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

if __name__ == "__main__":
    if initialize_database():
        print("Database initialized successfully!")
        sys.exit(0)
    else:
        print("Database initialization failed.")
        sys.exit(1)