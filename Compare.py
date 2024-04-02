import pypyodbc
import xml.etree.ElementTree as ET

# Function to execute SQL queries in Sybase DB
def execute_sql_queries(connection_string, queries):
    try:
        conn = pypyodbc.connect(connection_string)
        cursor = conn.cursor()

        for query in queries:
            cursor.execute(query)
            rows = cursor.fetchall()
            print("Results for query:", query)
            for row in rows:
                print(row)

        cursor.close()
        conn.close()
    except pypyodbc.Error as e:
        print("Database error:", e)

# Function to compare keywords from XML with SQL query outputs
def compare_keywords_with_sql_output(xml_file, keywords):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for keyword in keywords:
            found = False
            for child in root.iter():
                if child.text == keyword:
                    found = True
                    break
            if found:
                print(f"Keyword '{keyword}' found in XML")
            else:
                print(f"Keyword '{keyword}' not found in XML")

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

    # Define keywords to compare with XML
    xml_file_path = "your_xml_file.xml"
    keywords_to_compare = ["keyword1", "keyword2", "keyword3"]

    # Execute SQL queries
    execute_sql_queries(sybase_connection_string, sql_queries)

    # Compare keywords with XML
    compare_keywords_with_sql_output(xml_file_path, keywords_to_compare)
