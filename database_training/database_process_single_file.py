import os
import pandas as pd
from datetime import datetime
from database_training.email_format_extracter import get_email_formats

def process_single_file(input_file, output_folder):
    try:
        # Get the current date for the output filename
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Check if the output folder exists; if not, create it
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the file name without the extension
        file_name_only, file_extension = os.path.splitext(os.path.basename(input_file))

        print("Processing file:", file_name_only)

        # Check if the file is a supported format (CSV or Excel)
        if file_extension.lower() in ['.csv', '.xls', '.xlsx']:
            try:
                print ("I am in single process file")
                processed_data = get_email_formats(input_file)
                print ("get_email_formats")
                # Get the number of rows in processed data
                num_rows = len(processed_data)
                print(f"Number of rows processed: {num_rows}")

                # Save output file
                output_file_name = f"{file_name_only}_{current_date}_output.csv"
                output_file_path = os.path.join(output_folder, output_file_name)
                processed_data.to_csv(output_file_path, index=False)

                print(f"Processed data saved to: {output_file_path}")

            except Exception as e:
                print(f"Error processing file {input_file}: {e}")
        else:
            print(f"Unsupported file type: {file_extension}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# # Example usage
# input_file = "path/to/your/file.csv"  # Replace with the actual file path
# output_folder = "path/to/output/folder"  # Replace with the output folder path
# process_single_file(input_file, output_folder)
