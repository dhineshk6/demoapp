import xml.etree.ElementTree as ET
import sybpydb

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

# Define your SQL queries
sql_queries = [
    "SELECT column1 FROM your_table1 WHERE condition",
    "SELECT column2 FROM your_table2 WHERE condition",
    # Add more queries as needed
]

# Execute SQL queries
results = []
for query in sql_queries:
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Assuming you are fetching a single value
    results.append(result)
    cursor.close()

# Close the database connection
conn.close()

# Read the particular number from XML file
tree = ET.parse('your_xml_file.xml')
root = tree.getroot()
xml_number = int(root.find('.//number').text)  # Replace 'number' with the actual tag name

# Compare SQL results with XML number
for i, result in enumerate(results):
    if result == xml_number:
        print(f"Query {i+1}: Match! Number from XML: {xml_number}, Number from SQL: {result}")
    else:
        print(f"Query {i+1}: Mismatch! Number from XML: {xml_number}, Number from SQL: {result}")
