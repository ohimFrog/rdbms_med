import os
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

db_url = os.getenv("DATABASE_URL")
parsed = urlparse(db_url)

# Extract connection details
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 3306
db_name = parsed.path.lstrip('/')

print(f"Connecting to MySQL at {host}:{port} as {user}...")

try:
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
        
    conn.commit()
    conn.close()
    
except Exception as e:
    print(f"Error creating database: {e}")
