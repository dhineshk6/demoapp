import pymssql
import xml.etree.ElementTree as ET

# Function to establish connection to Sybase database
def connect_to_db(server, database, username, password):
    conn = pymssql.connect(server, username, password, database)
    cursor = conn.cursor()
    return conn, cursor

# Function to execute SQL queries and return results
def execute_sql(cursor, sql):
    cursor.execute(sql)
    return cursor.fetchall()

# Function to compare XML numbers with SQL query output
def compare_xml_with_sql(xml_data, sql_results):
    xml_numbers = [int(node.text) for node in xml_data.findall('.//number')]
    sql_numbers = [result[0] for result in sql_results]
    return xml_numbers == sql_numbers

# Function to parse XML from file
def parse_xml_from_file(file_path):
    tree = ET.parse(file_path)
    return tree.getroot()

# Main function
def main():
    # Database connection parameters
    server = 'your_server'
    database = 'your_database'
    username = 'your_username'
    password = 'your_password'

    # Path to XML file
    xml_file_path = 'path_to_your_xml_file.xml'

    # SQL queries
    sql_queries = [
        "SELECT COUNT(*) FROM your_table WHERE condition1",
        "SELECT COUNT(*) FROM your_table WHERE condition2",
        # Add more queries as needed
    ]

    try:
        # Connect to the database
        conn, cursor = connect_to_db(server, database, username, password)

        # Parse XML from file
        xml_data = parse_xml_from_file(xml_file_path)

        # Execute SQL queries and compare with XML data
        for sql_query in sql_queries:
            sql_results = execute_sql(cursor, sql_query)
            result = compare_xml_with_sql(xml_data, sql_results)
            print(f"Comparison result for query '{sql_query}': {result}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close connection
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
