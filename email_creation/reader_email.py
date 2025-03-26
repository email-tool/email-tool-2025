import pandas as pd
import os


import pandas as pd
import os,re

def process_file(file_path):
    # Determine file extension
    _, file_extension = os.path.splitext(file_path)
    
    # Load the data
    if file_extension == ".csv":
        data = pd.read_csv(file_path)
    elif file_extension in [".xls", ".xlsx"]:
        # Read up to 5 sheets and append data into one DataFrame
        excel_data = pd.ExcelFile(file_path)
        sheets = excel_data.sheet_names[:5]  # Get the first 5 sheets
        data = pd.concat([excel_data.parse(sheet) for sheet in sheets], ignore_index=True)
    else:
        raise ValueError("Unsupported file format. Only CSV and Excel files are allowed.")
    
    # Define the required columns
    required_columns = ["Company", "Contact Name"]
    all_columns = ["Srl No", "Company", "Contact Name", "First Name", "Last Name",
                   "Designation", "Location", "Industry", "Mailer_Status"]

    # Check for missing required columns
    missing_required_columns = [col for col in required_columns if col not in data.columns]
    if missing_required_columns:
        raise ValueError(f"Missing mandatory columns: {', '.join(missing_required_columns)}")
    
    # If "First Name" and "Last Name" are missing, create them by splitting "Contact Name"
    if "First Name" not in data.columns or "Last Name" not in data.columns:
        if "Contact Name" in data.columns:
            # Split the "Contact Name" into "First Name" and "Last Name"
            split_names = data["Contact Name"].str.split(" ", n=1, expand=True)
            data["First Name"] = split_names[0].apply(lambda x: re.sub(r'^[^a-zA-Z]+', '', x))
            data["Last Name"] = data['Contact Name'].apply(lambda x: x.split()[-1])
    
    # Add any missing non-mandatory columns and fill with "NA"
    for col in all_columns:
        if col not in data.columns:
            data[col] = "NA"
    
    # # Preprocess: Convert all text columns to lowercase
    # for col in data.select_dtypes(include=["object"]).columns:
    #     data[col] = data[col].str.lower()
    
    return data


def reader(file_path):
    # Example usage
    try:
    
        processed_data = process_file(file_path)
        processed_data = processed_data[["Srl No", "Company", "Contact Name", "First Name", "Last Name",
                   "Designation", "Location", "Industry", "Mailer_Status"]]
        processed_data.dropna(subset=["Company", "Contact Name", "First Name", "Last Name"], inplace=True)
        print("Processed DataFrame:")
        return processed_data
    except ValueError as e:
        print(f"Error: {e}")
        return e
