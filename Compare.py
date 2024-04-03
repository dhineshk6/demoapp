import xml.etree.ElementTree as ET
import pyodbc

# Function to execute SQL queries in Sybase DB
def execute_sql_queries(connection_string, queries):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        results = []
        for query in queries:
            cursor.execute(query)
            rows = cursor.fetchall()
            results.append(rows)

        cursor.close()
        conn.close()
        return results

    except pyodbc.Error as e:
        print("Database error:", e)
        return None

# Function to compare the number from XML with SQL query outputs
def compare_number_with_sql_output(xml_file, expected_number, results):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        xml_number = int(root.find('number').text)

        sql_output_sum = sum(len(rows) for rows in results)
        
        if xml_number == sql_output_sum == expected_number:
            print("The number from XML matches the sum of SQL query outputs.")
        else:
            print("The number from XML does not match the sum of SQL query outputs.")

    except ET.ParseError as e:
        print("Error parsing XML:", e)

# Main function
if __name__ == "__main__":
    # Define your Sybase connection string
    sybase_connection_string = "DRIVER={Adaptive Server Enterprise};SERVER=<your_server_name>;PORT=<your_port>;DATABASE=<your_database>;UID=<your_username>;PWD=<your_password>"

    # Define SQL queries to execute
    sql_queries = [
        "SELECT * FROM your_table_1",
        "SELECT * FROM your_table_2"
    ]

    # Define the expected number from XML
    expected_number_from_xml = 10

    # Define XML file path
    xml_file_path = "your_xml_file.xml"

    # Execute SQL queries
    sql_results = execute_sql_queries(sybase_connection_string, sql_queries)

    if sql_results is not None:
        # Compare number with SQL output
        compare_number_with_sql_output(xml_file_path, expected_number_from_xml, sql_results)
