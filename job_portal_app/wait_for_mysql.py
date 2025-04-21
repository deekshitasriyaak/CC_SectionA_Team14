import pymysql
import time
import os
import sys
import subprocess

# Get database configuration from environment variables
db_config = {
    'host': os.getenv("JOB_DB_HOST", "job_db"),
    'user': os.getenv("JOB_DB_USER", "root"),
    'password': os.getenv("JOB_DB_PASSWORD", "chandu@123S"),
    'db': os.getenv("JOB_DB_NAME", "job_portal"),
}

def wait_for_mysql(config, max_attempts=30, delay=3):
    """Wait for MySQL to be available"""
    print(f"Waiting for MySQL at {config['host']} to be ready...")
    
    attempts = 0
    while attempts < max_attempts:
        try:
            # Try to establish a connection
            connection = pymysql.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                connect_timeout=5
            )
            connection.close()
            print(f"Successfully connected to MySQL at {config['host']}!")
            return True
        except pymysql.err.OperationalError as e:
            attempts += 1
            print(f"MySQL is not ready yet. Waiting... ({attempts}/{max_attempts})")
            print(f"Error: {e}")
            
            if attempts >= max_attempts:
                print(f"Error: Couldn't connect to MySQL after {max_attempts} attempts.")
                return False
                
            time.sleep(delay)
    
    return False

if __name__ == "__main__":
    if wait_for_mysql(db_config):
        print("MySQL is ready. Running initialization script...")
        # Run the initialization script
        result = subprocess.run(["python", "db_init.py"])
        sys.exit(result.returncode)
    else:
        print("Failed to connect to MySQL. Exiting.")
        sys.exit(1)