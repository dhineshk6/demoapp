import re

def extract_xml_tags(log_file_path, output_file_path):
    keyword = "Input XML"
    xml_tag_pattern = re.compile(r"<[^>]+>")
    multiple_xml_pattern = re.compile(r"(<[^>]+>.*<[^>]+>)")

    with open(log_file_path, 'r') as log_file, open(output_file_path, 'w') as output_file:
        for line in log_file:
            if keyword in line:
                # Find lines that contain multiple XML tags
                if multiple_xml_pattern.search(line):
                    # Find all XML tags in the line
                    xml_tags = xml_tag_pattern.findall(line)
                    
                    # Write each XML tag to the output file
                    for tag in xml_tags:
                        output_file.write(tag + '\n')

# Example usage
log_file_path = 'path/to/your/logfile.log'
output_file_path = 'path/to/your/outputfile.txt'
extract_xml_tags(log_file_path, output_file_path)
