import ibm_db
import xml.etree.ElementTree as ET

def connect_to_db():
    conn_str = "DATABASE=<database_name>;HOSTNAME=<hostname>;PORT=<port_number>;PROTOCOL=TCPIP;UID=<username>;PWD=<password>;"
    conn = ibm_db.connect(conn_str, "", "")
    return conn

def execute_sql_query(conn, query):
    stmt = ibm_db.exec_immediate(conn, query)
    result = ibm_db.fetch_both(stmt)
    results = []
    while result:
        results.append(result)
        result = ibm_db.fetch_both(stmt)
    return results

def parse_xml_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    keywords = []
    for keyword in root.findall('keyword'):
        keywords.append(keyword.text)
    return keywords

def compare_with_keywords(sql_results, keywords):
    matches = []
    for row in sql_results:
        for keyword in keywords:
            if keyword in row:
                matches.append((row, keyword))
    return matches

def main():
    conn = connect_to_db()
    sql_query = "<your_sql_query>"
    xml_file = "data.xml"  # Replace with your XML file path
    sql_results = execute_sql_query(conn, sql_query)
    keywords = parse_xml_file(xml_file)
    matches = compare_with_keywords(sql_results, keywords)
    if matches:
        print("Matches found:")
        for match in matches:
            print("Row:", match[0])
            print("Keyword:", match[1])
    else:
        print("No matches found.")

if __name__ == "__main__":
    main()
