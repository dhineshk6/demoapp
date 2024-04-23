import re

def extract_xml_from_log(file_path):
    xml_data = []
    with open(file_path, 'r') as file:
        order_number = 1
        xml_content = ""
        for line in file:
            xml_content += line
            if "<>" in line:
                xml_tags = re.findall(r'', xml_content, re.DOTALL)
                for xml_tag in xml_tags:
                    xml_data.append((order_number, xml_tag))
                    order_number += 1
                xml_content = ""
    return xml_data

def compare_xml(log_file1, log_file2):
    xml_data1 = extract_xml_from_log(log_file1)
    xml_data2 = extract_xml_from_log(log_file2)

    return xml_data1, xml_data2

def output_results(xml_data1, xml_data2, output_file):
    with open(output_file, 'w') as file:
        file.write("XML Tags from File 1:\n")
        for order_number, xml_tag in xml_data1:
            file.write(f"Order {order_number}: {xml_tag}\n")

        file.write("\nXML Tags from File 2:\n")
        for order_number, xml_tag in xml_data2:
            file.write(f"Order {order_number}: {xml_tag}\n")

        file.write("\nComparison:\n")
        matching_orders = []
        mismatching_orders = []
        for (order_number1, xml1), (order_number2, xml2) in zip(xml_data1, xml_data2):
            if xml1 == xml2:
                matching_orders.append(order_number1)
            else:
                mismatching_orders.append((order_number1, order_number2))

        if matching_orders:
            file.write("\nMatching Orders:\n")
            for order_number in matching_orders:
                file.write(f"Order {order_number}\n")

        if mismatching_orders:
            file.write("\nMismatching Orders:\n")
            for order_number1, order_number2 in mismatching_orders:
                file.write(f"Order {order_number1} from File 1 does not match Order {order_number2} from File 2\n")

if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"
    output_file = "comparison_output.txt"

    xml_data1, xml_data2 = compare_xml(file1, file2)
    output_results(xml_data1, xml_data2, output_file)

    print(f"Comparison output written to {output_file}")
