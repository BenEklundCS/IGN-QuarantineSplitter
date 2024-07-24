import os
import sys

# Get the header of a quarantine.xml file
def get_header(xml_file):
    header_lines = []
    for _ in range(3):
        line = xml_file.readline()
        header_lines.append(line)
    return ''.join(header_lines)

def write_part(file_name, part_number, output_dir, header, current_part):
    # Footer (hardcoded)
    footer = "   </data>\n</cachedata>"
    # Create the part file path
    part_file_path = os.path.join(output_dir, f'{file_name}_part_{part_number}.xml')
    # Generate and write the file!
    try:
        with open(part_file_path, 'w', encoding='utf-8') as part_file:
            part_file.write(header)
            part_file.write(''.join(current_part))
            part_file.write(footer)
        print(f"Written: {part_file_path}")
    except Exception as e:
        print(f"Error writing part file {part_file_path}: {e}")

def split_xml(file_path, output_dir, max_size_mb):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    max_size_bytes = max_size_mb * 1024 * 1024
    part_number = 1
    current_size = 0
    current_part = []
    try:
        with open(file_path, 'r', encoding='utf-8') as xml_file:
            # Get the header
            header = get_header(xml_file)

            # Get the name of the input file
            file_name = os.path.splitext(os.path.basename(file_path))[0]

            # Iterate over the xml_file
            for line in xml_file:

                # If we've reached the end of a scanclasset and we're about to go over max_size_bytes then we write that part to the output dir
                if '<scanclassset' in line and current_size + len(line.encode('utf-8')) > max_size_bytes:
                    # Write the part
                    write_part(file_name, part_number, output_dir, header, current_part)
                    # Increment the part_number used to name files
                    part_number += 1
                    # Reset current_part and current_size
                    current_part = []
                    current_size = 0

                # We've reached the end! Break the loop here to avoid appending the footer to the current_part. We already have it!
                elif '</data' in line:
                    write_part(file_name, part_number, output_dir, header, current_part)
                    break
                
                # Append otherwise and continue parsing!
                current_part.append(line)
                current_size += len(line.encode('utf-8'))

            # If anything is left over after parsing, write it.
            if current_part:
                write_part(file_name, part_number, output_dir, header, current_part)
                
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    # Make sure 4 cmdline args were provided
    if len(sys.argv) != 4:
        print("usage: ./qsplitter.py path/to/input_file.xml path/to/output_directory max_filesize_mb")
        sys.exit(1)
        
    # Read cmdline args
    input_file = sys.argv[1]
    output_directory = sys.argv[2]

    # Make sure max_filesize_mb is valid before sending it to split_xml
    try:
        max_filesize_mb = float(sys.argv[3])
        if max_filesize_mb <= 5:
            raise ValueError("Max file size must be greater than 5mb!") # To prevent any infinite loops, 5mb seems reasonable, 10mb is my reccomendation 
    except ValueError as e:
        print(f"Invalid max file size: {e}")
        sys.exit(1)
        
        
    split_xml(input_file, output_directory, max_filesize_mb)
