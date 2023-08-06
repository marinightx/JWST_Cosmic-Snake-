# Import necessary libraries
import glob
from astropy.io import fits
import os
import json
import sys
from jwst.pipeline import Spec2Pipeline
from jwst.pipeline import Spec3Pipeline

# Directory containing FITS files
input_dir = './'
json_dir = './'

# Lists to store created JSON file names and new JSON files
json_cree = []
nouveau_json = []

# Retrieve command-line arguments
args = sys.argv[1:]

"""in the command line, if only one argument is specified then we take the ifu data, if a second is specified then it is of sky type and if at the very beginning "--leakcal" is specified then the leakcal is applied to the arguemnts specified
"""
# Check if the argument --leakcal is specified 
if '--leakcal' in args:
    leakcal_arg_index = args.index('--leakcal')
    process_leakcal_files = True
else:
    leakcal_arg_index = -1
    process_leakcal_files = False

# Check if the first argument is specified
if len(args) > leakcal_arg_index + 1:
    science_arg = args[leakcal_arg_index + 1]  # Target type specified in the command-line
    process_ifu_files = True
else:
    print("No argument specified for the science type.")
    sys.exit(1)

# Check if the second argument is specified
if len(args) > leakcal_arg_index + 2:
    background_arg = args[leakcal_arg_index + 2]  # Target type specified in the command-line
    process_sky_files = True
else:
    background_arg = None
    process_sky_files = False

# Create the directory name based on the specified arguments
"""Addition of an extension in the output file according to what is specified on the command line """
output_dir = science_arg
if process_leakcal_files:
    output_dir += "_LEAK"
if process_sky_files:
    output_dir += "_SKY"

# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read all rate.fits files from the input directory 
fits_files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*", "*rate.fits"))

# Define lists for IFU files
ifu_files_nrs1 = []
leakcal_ifu_files_nrs1 = []
leakcal_sky_files_nrs1 = []
sky_files_nrs1 = []
ifu_files_nrs2 = []
leakcal_ifu_files_nrs2 = []
leakcal_sky_files_nrs2 = []
sky_files_nrs2 = []

# Iterate over all retrieved FITS files
for fits_file in fits_files:
    # Get FITS headers of the current file
    header = fits.getheader(fits_file)
    print("File:", fits_file)
    print(header)

    # Check if "TARGPROP" field is present in the header and if its value matches the specified target type from the command-line
#put the different ".fits" files in the lists created for the 2 detectors
    if "TARGPROP" in header:
        targprop_value = header["TARGPROP"]
        if targprop_value == science_arg:
            # If the detector value is "NRS1", also check the "IS_IMPRT" field
            if "DETECTOR" in header:
                detector = header["DETECTOR"]
                if detector == "NRS1":
                    if "IS_IMPRT" in header:
                        is_imprt_value = header["IS_IMPRT"]
                        # Add the current file to the appropriate list based on the value of "IS_IMPRT"
                        if is_imprt_value is True:
                            leakcal_ifu_files_nrs1.append(fits_file)
                        elif is_imprt_value is False:
                            ifu_files_nrs1.append(fits_file)
                # If the detector value is "NRS2", also check the "IS_IMPRT" field
                elif detector == "NRS2":
                    if "IS_IMPRT" in header:
                        is_imprt_value = header["IS_IMPRT"]
                        # Add the current file to the appropriate list based on the value of "IS_IMPRT"
                        if is_imprt_value is True:
                            leakcal_ifu_files_nrs2.append(fits_file)
                        elif is_imprt_value is False:
                            ifu_files_nrs2.append(fits_file)
        # If the "TARGPROP" value matches the argument for background files, perform similar actions for background files
        if targprop_value == background_arg:
            if "DETECTOR" in header:
                detector = header["DETECTOR"]
                if detector == "NRS1":
                    if "IS_IMPRT" in header:
                        is_imprt_value = header["IS_IMPRT"]
                        if is_imprt_value is True:
                            leakcal_sky_files_nrs1.append(fits_file)
                        elif is_imprt_value is False:
                            sky_files_nrs1.append(fits_file)
                elif detector == "NRS2":
                    if "IS_IMPRT" in header:
                        is_imprt_value = header["IS_IMPRT"]
                        if is_imprt_value is True:
                            leakcal_sky_files_nrs2.append(fits_file)
                        elif is_imprt_value is False:
                            sky_files_nrs2.append(fits_file)

# Print the number of IFU files for NRS1 and NRS2 detectors
print("Number of IFU files NRS1:", len(ifu_files_nrs1))
print("Number of IFU files NRS2:", len(ifu_files_nrs2))

# Processing files with NRS1 detector
for i, fits_file in enumerate(ifu_files_nrs1):
    # Get the FITS header of the current IFU file
    header = fits.getheader(fits_file)
    # Extract the filename without the extension
    filename = os.path.splitext(os.path.basename(fits_file))[0]
    # Create a JSON structure for file association
    association = {
        "asn_rule": "DMS_Level3_Base",
        "asn_pool": "none",
        "asn_type": "None",
        "products": [
            {
                "name": f"{filename}.json",
                "members": []
            }
        ]
    }

    # Add the current file to the members list, specifying the experiment type (science) if needed
    if process_ifu_files:
        association["products"][0]["members"].append({"expname": fits_file, "exptype": "science"})

    # Add leakcal calibration files if specified
    if process_leakcal_files:
        for leakcal_fits_file in leakcal_ifu_files_nrs1:
            association["products"][0]["members"].append({"expname": leakcal_fits_file, "exptype": "imprint"})

    # Add sky background files if specified
    if process_sky_files:
        for sky_fits_file in sky_files_nrs1:
            association["products"][0]["members"].append({"expname": sky_fits_file, "exptype": "background"})

        # Add leakcal calibration files for sky background if specified
        if process_leakcal_files:
            for leakcal_sky_fits_file in leakcal_sky_files_nrs1:
                association["products"][0]["members"].append({"expname": leakcal_sky_fits_file, "exptype": "imprint"})

    # Define the output JSON path
    output_json = os.path.join(output_dir, association["products"][0]["name"])

    # Write the JSON structure to the output JSON file
    with open(output_json, "w") as outfile:
        json.dump(association, outfile, indent=4)
        json_cree.append(output_json)
    print("Created .json file:", output_json)

# Processing files with NRS2 detector
for i, fits_file in enumerate(ifu_files_nrs2):
    # Get the FITS header of the current IFU file
    header = fits.getheader(fits_file)
    # Extract the filename without the extension
    filename = os.path.splitext(os.path.basename(fits_file))[0]
    # Create a JSON structure for file association
    association = {
        "asn_rule": "DMS_Level3_Base",
        "asn_pool": "none",
        "asn_type": "None",
        "products": [
            {
                "name": f"{filename}.json",
                "members": []
            }
        ]
    }

    # Add the current file to the members list, specifying the experiment type (science) if needed
    if process_ifu_files:
        association["products"][0]["members"].append({"expname": fits_file, "exptype": "science"})

    # Add leakcal calibration files if specified
    if process_leakcal_files:
        for leakcal_fits_file in leakcal_ifu_files_nrs2:
            association["products"][0]["members"].append({"expname": leakcal_fits_file, "exptype": "imprint"})

    # Add sky background files if specified
    if process_sky_files:
        for sky_fits_file in sky_files_nrs2:
            association["products"][0]["members"].append({"expname": sky_fits_file, "exptype": "background"})

        # Add leakcal calibration files for sky background if specified
        if process_leakcal_files:
            for leakcal_sky_fits_file in leakcal_sky_files_nrs2:
                association["products"][0]["members"].append({"expname": leakcal_sky_fits_file, "exptype": "imprint"})

    # Define the output JSON path
    output_json = os.path.join(output_dir, association["products"][0]["name"])

    # Write the JSON structure to the output JSON file
    with open(output_json, "w") as outfile:
        json.dump(association, outfile, indent=4)
        json_cree.append(output_json)
    print("Created .json file:", output_json)

# Processing files with NRS2 detector
for i, fits_file in enumerate(ifu_files_nrs2):
    # Get the FITS header of the current IFU file
    header = fits.getheader(fits_file)
    # Extract the filename without the extension
    filename = os.path.splitext(os.path.basename(fits_file))[0]
    # Create a JSON structure for file association
    association = {
        "asn_rule": "DMS_Level3_Base",
        "asn_pool": "none",
        "asn_type": "None",
        "products": [
            {
                "name": f"{filename}.json",
                "members": []
            }
        ]
    }

    # Add the current file to the members list, specifying the experiment type (science) if needed
    if process_ifu_files:
        association["products"][0]["members"].append({"expname": fits_file, "exptype": "science"})

    # Add leakcal calibration files if specified
    if process_leakcal_files:
        for leakcal_fits_file in leakcal_ifu_files_nrs2:
            association["products"][0]["members"].append({"expname": leakcal_fits_file, "exptype": "imprint"})

    # Add sky background files if specified
    if process_sky_files:
        for sky_fits_file in sky_files_nrs2:
            association["products"][0]["members"].append({"expname": sky_fits_file, "exptype": "background"})

        # Add leakcal calibration files for sky background if specified
        if process_leakcal_files:
            for leakcal_sky_fits_file in leakcal_sky_files_nrs2:
                association["products"][0]["members"].append({"expname": leakcal_sky_fits_file, "exptype": "imprint"})

    # Define the output JSON path
    output_json = os.path.join(output_dir, association["products"][0]["name"])

    # Write the JSON structure to the output JSON file
    with open(output_json, "w") as outfile:
        json.dump(association, outfile, indent=4)
        json_cree.append(output_json)
    print("Created .json file:", output_json)

"""
for json_file in json_cree:
    spec2_pipeline = Spec2Pipeline()
    spec2_pipeline.call(json_file, save_results=True, output_dir=output_dir)
"""
"""
# Ajouter les fichiers "cal.fits" au fichier JSON
directory = output_dir
# Liste tous les fichiers du répertoire
files = os.listdir(directory)

# Filtrer les fichiers qui se terminent par "cal.fits"
cal_files = [filename for filename in files if filename.endswith("cal.fits")]

# Afficher la liste des fichiers "cal.fits"
for filename in cal_files:
    print(filename)
# Creation of the JSON structure
json_for_spec3 = {
    "asn_rule": "DMS_Level3_Base",
    "asn_pool": "none",
    "asn_type": "None",
    "products": [
        {
            "name": "calibration_files.json",
            "members": []
        }
    ]
}

# Liste tous les fichiers du répertoire
files = os.listdir(directory)

# Parcourt les fichiers et ajoute ceux qui se terminent par "cal.fits" au JSON
for filename in files:
    if filename.endswith("cal.fits"):
        file_path = os.path.join(directory, filename)
        json_for_spec3["products"][0]["members"].append({"expname": file_path, "exptype": "science"})

# Enregistre le fichier JSON
json_path = os.path.join(directory, json_for_spec3["products"][0]["name"])
with open(json_path, "w") as outfile:
    json.dump(json_for_spec3, outfile, indent=4)

print("Le fichier JSON pour les fichiers 'cal.fits' a été créé :", json_path)
"""
files = os.listdir(output_dir)

# Filter the files that end with 'cal.fits'
cal_files = [filename for filename in files if filename.endswith("cal.fits")]

# Display the list of 'cal.fits' files.
for filename in cal_files:
    print(filename)

# Creation of the JSON structure.
json_for_spec3 = {
    "asn_rule": "DMS_Level3_Base",
    "asn_pool": "none",
    "asn_type": "None",
    "products": [
        {
            "name": "calibration_files.json",
            "members": []
        }
    ]
}

# Traverse the files and add those ending with 'cal.fits' to the JSON.
for filename in cal_files:
    file_path = os.path.join(filename)
    json_for_spec3["products"][0]["members"].append({"expname": file_path, "exptype": "science"})

# Save the JSON file.
json_path = os.path.join(output_dir, json_for_spec3["products"][0]["name"])
with open(json_path, "w") as outfile:
    json.dump(json_for_spec3, outfile, indent=4)
print("output_dir", output_dir)
print("Le fichier JSON pour les fichiers 'cal.fits' a été créé :", json_path)
calibration_json_path = os.path.join(output_dir, "calibration_files.json")

""" Cube build processing using Spec3Pipeline
Create and run the Spec3Pipeline with specific parameters."""


spec3_pipeline = Spec3Pipeline()
spec3_pipeline.cube_build.coord_system = 'ifualign' #Aligning based on IFU instead of the sky, as the sky is the default parameter.
spec3_pipeline.cube_build.scale1 = 0.075 #reduce the pixel size
spec3_pipeline.cube_build.scale2 = 0.075 #reduce the pixel size
spec3_pipeline.save_results = 'True'
spec3_pipeline.output_dir = output_dir
result = spec3_pipeline.run(calibration_json_path)
#result.save(output_dir)
#spec3_pipeline.call(calibration_json_path, save_results=True, output_dir=output_dir)
