# DATA REDUCTION WITH THE JWST SCIENCE CALIBRATION PIPELINE 

This program is designed to filter and process specific FITS files, create JSON structures for data association, and perform cube processing using the Spec2Pipeline and Spec3Pipeline.

# Installation

No installation is required to run this program as it solely uses standard Python libraries. Just ensure you have Python installed on your system.

# Usage

Place the FITS files in the input directory specified by input_dir.
Run the program using the following command:

    python program_name.py [--leakcal] argument1 argument2 

program_name.py : in my case it's creation_json_step2_3.py
argument1: Science file type specified on the command line.

argument2: Sky file type specified on the command line.

--leakcal (optional): If this option is specified, the program will apply the leakcal file to the specified arguments.

Filtered files and JSON structures will be created in the output directory specified by output_dir.

# Configurable Parameters

You can adjust the following parameters in the program:

    cube_build.scale1: Reduce pixel size on axis 1 for cube processing.
    cube_build.scale2: Reduce pixel size on axis 2 for cube processing.
    cube_build.coord_system : as the sky is the default parameter.


# Examples

To process IFU type files:

    python creation_json_step2_3.py ifu

To process IFU type files with sky files using the leakcal file:

    python creation_json_step2_3.py --leakcal ifu sky 

# Notes
    Ensure all required FITS files are present in the specified input directory.
    Created files will be saved in the specified output directory.
    Please check the comments in the code for more details about different parts of the program.

# Authors

Marina Serre
