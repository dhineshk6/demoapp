import re

def extract_xml_from_log(file_path):
    xml_data = []
    with open(file_path, 'r') as file:
        xml_content = ""
        for line in file:
            xml_content += line
            if "<>" in line:
                xml_tags = re.findall(r'', xml_content, re.DOTALL)
                xml_data.extend(xml_tags)
                xml_content = ""
    return xml_data

def compare_xml(log_file1, log_file2):
    xml_data1 = extract_xml_from_log(log_file1)
    xml_data2 = extract_xml_from_log(log_file2)

    return xml_data1, xml_data2

def output_results(xml_data1, xml_data2, output_file):
    with open(output_file, 'w') as file:
        file.write("XML Tags from File 1:\n")
        for xml_tag in xml_data1:
            file.write(xml_tag + '\n')

        file.write("\nXML Tags from File 2:\n")
        for xml_tag in xml_data2:
            file.write(xml_tag + '\n')

        file.write("\nComparison:\n")
        for i, (xml1, xml2) in enumerate(zip(xml_data1, xml_data2), start=1):
            file.write(f"\nComparison {i}:\n")
            if xml1 == xml2:
                file.write("XML tags match.\n")
            else:
                file.write("XML tags do not match.\n")

if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"
    output_file = "comparison_output.txt"

    xml_data1, xml_data2 = compare_xml(file1, file2)
    output_results(xml_data1, xml_data2, output_file)

    print(f"Comparison output written to {output_file}")
