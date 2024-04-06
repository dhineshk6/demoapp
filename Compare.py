
db2 "SELECT STMT_TEXT, STMT_START, STMT_END, STMT_EXECUTION_STATUS FROM SYSCAT.STATEMENT_HISTORY ORDER BY STMT_START DESC FETCH FIRST 10 ROWS ONLY"
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

# Define the particular value from the log file
desired_log_value = 'desired_value'  # Update with the desired value from the log file

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

# Compare SQL results with the particular value from the log file
for i, query_result in enumerate(query_results, start=1):
    if desired_log_value == str(query_result):  # Comparing log value with each SQL query result
        print(f"Query {i}: Match! Desired Value from Log: {desired_log_value}, Value from SQL: {query_result}")
    else:
        print(f"Query {i}: Mismatch! Desired Value from Log: {desired_log_value}, Value from SQL: {query_result}")
