# /**
# * MIT License
# * Copyright (c) 2022 Javier I. Acosta M.
# * Permission is hereby granted, free of charge, to any person obtaining a copy
# * of this software and associated documentation files (the "Software"), to deal
# * in the Software without restriction, including without limitation the rights
# * to use, copy, modify, merge, publish, distribute, sub-license, and/or sell
# * copies of the Software, and to permit persons to whom the Software is
# * furnished to do so, subject to the following conditions:
# *
# * The above copyright notice and this permission notice shall be included in all
# * copies or substantial portions of the Software.
# *
# * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# * SOFTWARE.
# */
import getopt
import pathlib
import re
import os
import sys
import logging


class Globals:
    num_updates = 0
    num_header_files = 0
    num_header_files_entries = 0
    num_warnings = 0


class FileHeaderEntry(object):
    """
    Ancillary class for the dictionary entry
    """
    def __init__(self, filename: str):
        """

        :param filename:
        """
        self.filename_key: str = filename
        self.associated_files = []


def process_headers(filename_src: str, filename_dst: str):
    """
    Process a given header file
    :param filename_src: The source file to be processed
    :param filename_dst: The output file where the updated header will be placed
    """
    ext = [".h", ".cpp", ".hpp", ".c"]
    if not filename_src.endswith(tuple(ext)):
        return
    logging.debug("Processing " + filename_src)
    Globals.num_header_files += 1

    # Create the output directory (if it does not exist)
    path = pathlib.Path(filename_dst)
    parent_dir = path.parent.absolute()
    pathlib.Path(parent_dir).mkdir(parents=True, exist_ok=True)

    file_input = open(filename_src, "r")
    file_output = open(filename_dst, "w")
    lines = file_input.readlines()
    for line in lines:
        new_line = line
        if "#include" in line:
            Globals.num_header_files_entries += 1
            try:
                pattern = '"(.+?)"'
                header_file = re.search(pattern, line).group(1)
                logging.debug("\t" + header_file)
                # Extract the header file alone ( no indirections)
                header_file = os.path.basename(header_file)
                # replace with include from header dd
                lookup: FileHeaderEntry = header_db[header_file]
                if lookup is not None:
                    if len(lookup.associated_files) > 1:
                        Globals.num_warnings += 1
                        logging.waring("User input needed")
                        logging.waring("\tThere Multiple options for" + filename_dst + "defaulted to [0]")
                        logging.waring("\t" + lookup.associated_files)
                        logging.waring("\t" + "before" + header_file)
                    # Replace
                    new_header = "\"" + str(lookup.associated_files[0]).replace("\\", "/") + "\""
                    new_line = re.sub(pattern, new_header, line, count=1)
                if line != new_line:
                    logging.debug("\tOld line " + line.rstrip('\n'))
                    logging.debug("\tNew line " + new_line.rstrip('\n'))
                    Globals.num_updates += 1
                else:
                    logging.debug("Not updated")
            except:
                # System
                pass
        file_output.write(new_line)
    # Close files
    file_input.close()
    file_output.close()


def load_all_headers(include_list):
    """
    Load the header file database
    :param include_list: List of directories from where to look for header files
    """
    header_db_local: dict = {}
    for include_root in include_list:
        for root, sub_dirs, files in os.walk(include_root):
            for filename in files:
                if filename.endswith(".h"):
                    filename_src_rel = os.path.relpath(os.path.join(root, filename), include_root)
                    if filename in header_db_local:
                        db_entry: FileHeaderEntry = header_db_local[filename]
                        db_entry.associated_files.append(filename_src_rel)
                    else:
                        db_entry = FileHeaderEntry(filename)
                        db_entry.associated_files.append(filename_src_rel)
                        header_db_local[filename] = db_entry
    return header_db_local


def print_usage():
    """
    Prints usage message     
    """
    print('Usage: ' + os.path.basename(sys.argv[0]) + ' [options] -i <include file> -s <source-dir> -o <output-dir>')
    print('Options:')
    print('\t-h, --help    : Show this message')
    print('\t-i, --includes: Include directories separated by ";" (mandatory)')
    print('\t-s, --source  : Sources directory to be processed (mandatory)')
    print('\t-o, --output  : Output directory (mandatory)')
    print('\t-v, --verbose : Verbose actions (optional)')
    print('Sample: python .\include-fixer.py -s \"C:\\library-xxxx\\source\" -i \"C:\\library-xxxx\\external-references;C:\\library-yyyy\include\" -o \"C:\\fixed-include\output\"')

if __name__ == "__main__":
    debug = False

    # Remove 1st argument from the list of command line arguments
    argument_list = sys.argv[1:]

    # Options
    options = "hvi:s:o:"
    num_mandatory = 3
    num_mandatory_count = 0
    # Parameters
    includes = ""
    source_dir = ""
    output_dir = ""

    # Long options
    long_options = ["--help", "--verbose", "--includes", "--source", "--output"]

    # Make sure the number of arguments match
    if len(sys.argv) - 1 < num_mandatory:
        print_usage()
        exit(0)
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argument_list, options, long_options)
        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--help"):
                print_usage()
            if currentArgument in ("-v", "--verbose"):
                debug = True
            elif currentArgument in ("-i", "--includes"):
                print("Include: ", currentValue)
                includes = currentValue
                num_mandatory_count += 1
            elif currentArgument in ("-s", "--source"):
                print("Source: ", currentValue)
                source_dir = currentValue
                num_mandatory_count += 1

            elif currentArgument in ("-o", "--output"):
                print("Output: ", currentValue)
                output_dir = currentValue
                num_mandatory_count += 1
    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))

    if num_mandatory_count != num_mandatory:
        print_usage()
        exit(0)

    # Setup verbose level
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    # Create include database
    include_list = includes.split(";")
    include_list.append(source_dir)
    header_db = load_all_headers(include_list)

    # Process input source directory
    for root, sub_dirs, files in os.walk(source_dir):
        for filename in files:
            filename_src = os.path.join(root, filename)
            filename_src_rel = os.path.relpath(os.path.join(root, filename), source_dir)
            filename_dst = os.path.join(output_dir, filename_src_rel)
            process_headers(filename_src, filename_dst)

    logging.info("Summary")
    logging.info("Num files inspected : " + str(Globals.num_header_files))
    logging.info("Num #include entries: " + str(Globals.num_header_files_entries))
    logging.info("Num updates needed  : " + str(Globals.num_updates))
    logging.info("Num warnings        : " + str(Globals.num_warnings))

