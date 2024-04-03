import sybpydb

# Define your database connection parameters
connection_params = {
    'userid': 'your_username',
    'password': 'your_password',
    'servername': 'your_server',
    'port': 5000,  # Adjust port number if necessary
    'dbname': 'your_db'
}

# Define the log file path
log_file_path = '/path/to/your/log_file.log'  # Update with the actual path to your log file

# Define your SQL queries
sql_queries = [
    "SELECT column1 FROM your_table1 WHERE condition1",
    "SELECT column2 FROM your_table2 WHERE condition2",
    # Add more queries as needed
]

# Establish database connection
conn = sybpydb.connect(**connection_params)

# Execute SQL queries
query_results = []
for query in sql_queries:
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Assuming you are fetching a single value
    query_results.append(result)
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

# Compare SQL results with value from log file
for i, (sql_result, query_result) in enumerate(zip(log_value, query_results), start=1):
    if sql_result == query_result:
        print(f"Query {i}: Match! Value from Log: {sql_result}, Value from SQL: {query_result}")
    else:
        print(f"Query {i}: Mismatch! Value from Log: {sql_result}, Value from SQL: {query_result}")
