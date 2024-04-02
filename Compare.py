import custom_sql_connector as sql
import xml.etree.ElementTree as ET

# Function to execute SQL queries
def execute_sql_queries(connection, queries):
    try:
        results = []
        for query in queries:
            result = connection.execute(query)
            rows = result.fetchall()
            results.append(rows)
        return results
    except Exception as e:
        print("Error executing SQL query:", e)
        return None

# Function to compare numbers from XML with SQL query outputs
def compare_numbers_with_sql_output(xml_file, expected_numbers, results):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Retrieve numbers from XML
        xml_numbers = [int(element.text) for element in root.findall('number')]

        # Check if the number of XML numbers matches the number of SQL queries executed
        if len(xml_numbers) != len(results):
            print("Error: Number of XML numbers does not match the number of SQL queries.")
            return

        # Compare each number from XML with the corresponding SQL output
        for i, xml_number in enumerate(xml_numbers):
            sql_output_sum = sum(len(rows) for rows in results[i])
            if xml_number == sql_output_sum == expected_numbers[i]:
                print(f"XML number {i+1} matches the sum of SQL query {i+1} outputs.")
            else:
                print(f"XML number {i+1} does not match the sum of SQL query {i+1} outputs.")

    except ET.ParseError as e:
        print("Error parsing XML:", e)

# Main function
if __name__ == "__main__":
    # Create your SQL connection
    sql_connection = sql.create_connection("<connection_parameters>")

    # Define SQL queries to execute
    sql_queries = [
        "SELECT * FROM your_table_1",
        "SELECT * FROM your_table_2"
    ]

    # Define the expected numbers from XML
    expected_numbers_from_xml = [10, 20]  # Example: [10, 20] means we expect two numbers, 10 and 20.

    # Define XML file path
    xml_file_path = "your_xml_file.xml"

    # Execute SQL queries
    sql_results = execute_sql_queries(sql_connection, sql_queries)

    if sql_results is not None:
        # Compare numbers with SQL output
        compare_numbers_with_sql_output(xml_file_path, expected_numbers_from_xml, sql_results)

    # Close SQL connection
    sql.close_connection(sql_connection)
