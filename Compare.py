import sybpydb
import sys

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: python script.py <log_file_path>")
    sys.exit(1)

log_file_path = sys.argv[1]

# Define your database connection parameters
connection_params = {
    'userid': 'your_username',
    'password': 'your_password',
    'servername': 'your_server',
    'port': 5000,  # Adjust port number if necessary
    'dbname': 'your_db'
}

# Establish database connection
conn = sybpydb.connect(**connection_params)

# Define your SQL query
sql_query = "SELECT your_column FROM your_table WHERE condition"

# Execute SQL query
cursor = conn.cursor()
cursor.execute(sql_query)
sql_result = cursor.fetchone()[0]  # Assuming you are fetching a single value
cursor.close()

# Close the database connection
conn.close()

# Read value from log file
log_value = None
with open(log_file_path, 'r') as log_file:
    for line in log_file:
        if line.strip() == 'desired_value':
            log_value = line.strip()
            break

# Compare SQL result with value from log file
if log_value is not None:
    if sql_result == log_value:
        print(f"Match! Value from Log: {log_value}, Value from SQL: {sql_result}")
    else:
        print(f"Mismatch! Value from Log: {log_value}, Value from SQL: {sql_result}")
else:
    print("Desired value not found in log file.")
