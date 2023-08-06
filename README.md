# DATA REDUCTION WITH THE JWST SCIENCE CALIBRATION PIPELINE 

This program is designed to filter and process specific FITS files, create JSON structures for data association, and perform cube processing using the Spec2Pipeline and Spec3Pipeline.

# Installation

No installation is required to run this program as it solely uses standard Python libraries. Just ensure you have Python (version X.X or higher) installed on your system.
Usage

    Place the FITS files in the input directory specified by input_dir.
    Run the program using the following command:

bash

    python program_name.py [--leakcal] argument1 argument2 
    argument1: Science file type specified on the command line.
    argument2: Sky file type specified on the command line.
    --leakcal (optional): If this option is specified, the program will apply the leakcal file to the specified arguments.

    Filtered files and JSON structures will be created in the output directory specified by output_dir.
