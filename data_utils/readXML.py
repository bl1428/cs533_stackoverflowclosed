import os
import time
import xml.etree.cElementTree as ET


def get_file_size_in_mb(file_name):
    """
    Method to check the file size in MB
    """
    file_size = 0
    if os.path.isfile(file_name):
        file_size = os.path.getsize(file_name) # Get the file size
        file_size = round(file_size / (1024 * 1024.0), 2) # Convert into MB
    file_size = '{:,.2f}'.format(file_size)
    return str(file_size) + ' MB'


def read_xml_file(xml_file, element):
    """
    Parse the xml file to xml.etree.cElementTree
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    number_of_element = len(root.findall(element))
    return '{:,.0f}'.format(number_of_element)


def read_xml_file_line_basis(xml_file, element):
    """
    Read the xml file and capture only the elements we need.
    """
    start_tag = f'<{element}>' # 3
    end_tag = f'</{element}>' # 2
    start_tag_identified = False # 3
    captured_records = list() # 4
    captured_line = ''
    with open(xml_file) as f: # 5
        for line in f: # 6
            if start_tag in line: # 7
                start_tag_identified = True
            if start_tag_identified: # 8
                captured_line += line
            if end_tag in line: # 9
                captured_records.append(captured_line)
                start_tag_identified = False # 10
                captured_line = '' # 10
    return '{:,.0f}'.format(len(captured_records))


if __name__ == '__main__':
    xml_file_name = './datasets/Posts.xml'
    print(f'File Size: {get_file_size_in_mb(xml_file_name)}')
    start_time = time.perf_counter()
    counter = read_xml_file(xml_file_name, 'ProteinEntry/header')
    end_time = time.perf_counter()
    total_time = round(end_time - start_time, 2)
    print(f'xml.etree.cElementTree - Total time taken:[{total_time}] seconds to identify the number of elements: [{counter}]')
    print("<---------------------------------------->")
    start_time = time.perf_counter()
    counter = read_xml_file_line_basis(xml_file_name, 'header')
    end_time = time.perf_counter()
    total_time = round(end_time - start_time, 2)
    print(f'Customized XML Read - Total time taken:[{total_time}] seconds to identify the number of elements: [{counter}]')