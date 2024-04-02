import xml.etree.ElementTree as ET
import mysql.connector  # Replace with your SQL library if needed

def get_keyword_from_xml(xml_file):
  """
  Parses the specified XML file and returns the value of the first element with the 'keyword' tag.

  Args:
      xml_file (str): Path to the XML file.

  Returns:
      str: The keyword value from the XML file, or None if not found.
  """
  try:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root.find('keyword').text
  except FileNotFoundError:
    print(f"Error: XML file '{xml_file}' not found.")
    return None
  except Exception as e:
    print(f"Error parsing XML file: {e}")
    return None

def execute_sql_query(sql_query, sql_params):
  """
  Executes the provided SQL query with the given parameters and returns all results as a list of dictionaries.

  Args:
      sql_query (str): The SQL query to execute.
      sql_params (tuple): A tuple containing the parameters for the query (optional).

  Returns:
      list: A list of dictionaries containing the results from the query, with column names as keys.
  """
  # Replace with your preferred SQL library connection and execution logic
  try:
    connection = mysql.connector.connect(  # Replace connection details
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )
    cursor = connection.cursor()
    cursor.execute(sql_query, sql_params)
    column_names = [desc[0] for desc in cursor.description]  # Get column names
    results = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    connection.close()
    return results
  except Exception as e:
    print(f"Error executing SQL query: {e}")
    return []

def main():
  xml_file = "your_file.xml"  # Replace with your XML file path
  sql_queries = [  # List of SQL queries to execute
      "SELECT * FROM table1 WHERE id = %s",
      "SELECT * FROM table2 WHERE key = %s"
  ]
  sql_params = (1,)  # Replace with your SQL query parameter (optional)

  keyword = get_keyword_from_xml(xml_file)
  if keyword:
    all_results = []
    for query in sql_queries:
      results = execute_sql_query(query, sql_params)
      all_results.extend(results)  # Combine results from all queries

    if all_results:
      print(f"Keyword from XML: {keyword}")
      print("SQL Query Results:")
      for result in all_results:
        print(result)  # Print entire dictionary for each row
      match_found = False
      for result in all_results:
        if keyword in result.values():  # Check if keyword exists in any column value
          match_found = True
          break
      if match_found:
        print("Keyword matches at least one value in SQL query output!")
      else:
        print("Keyword does not match any value in SQL query output.")
    else:
      print("No results found from any SQL queries.")
  else:
    print("Error retrieving keyword from XML file.")

if __name__ == "__main__":
  main()
