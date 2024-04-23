import re

def extract_xml_from_log(file_path):
    xml_data = []
    with open(file_path, 'r') as file:
        for line in file:
            xml_match = re.search(r'xml:\s*(.+)', line)
            if xml_match:
                xml_content = xml_match.group(1)
                xml_data.append(xml_content)
    return xml_data

def compare_xml(log_file1, log_file2):
    xml_data1 = extract_xml_from_log(log_file1)
    xml_data2 = extract_xml_from_log(log_file2)

    return xml_data1, xml_data2

def output_results(xml_data1, xml_data2):
    print("XML Data from File 1:")
    for xml_content in xml_data1:
        print(xml_content)

    print("\nXML Data from File 2:")
    for xml_content in xml_data2:
        print(xml_content)

    print("\nComparison:")
    for i, (xml1, xml2) in enumerate(zip(xml_data1, xml_data2), start=1):
        print(f"\nComparison {i}:")
        if xml1 == xml2:
            print("XML content matches.")
        else:
            print("XML content does not match.")

if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"

    xml_data1, xml_data2 = compare_xml(file1, file2)
    output_results(xml_data1, xml_data2)
