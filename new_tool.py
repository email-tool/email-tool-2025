import os,pickle
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from helper.csv_excel_loader import file_load
from email_verifier.email_verifier import verify_app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
from database_training.database_process_mutifile import process_files_and_save_output

import pandas as pd
from database_training.update_db_manually import update_pickle
from email_creation.create_emails import email_creator_app
from database_training.database_process_single_file import process_single_file
from automatic_email_format import scrapper_run
from automatic_email_format.scarpper_manager import scrapper_manager 
from automatic_email_format.get_email_flags import get_flags
from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")
log_file_path = "log.txt"  # Log file to read
import logging

log = logging.getLogger("werkzeug")
handler = logging.FileHandler("flask_access.log")  # Save logs in this file
log.addHandler(handler)
log.setLevel(logging.INFO)  # You can change to ERROR if you only want errors


'''
----------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''
@app.route('/')
def dashboard():
    return render_template('dashboard.html')


'''
------------------------------------------------------------Database-----------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''


import os

# Get the full path of the script
script_path = os.path.abspath('appy.py')
# Get the directory containing the script
user_path = os.path.dirname(script_path)
print("Base directory:", user_path)
base_path = user_path+"/files/"
Source_file_path = base_path+'database_source_files'
Output_files_path = base_path+'database_output_files'
new_db_pickle_file_path = base_path+'main_database//'+'new_db.pkl'
old_db_pickle_file_path = base_path+'main_database//'+'old_db.pkl'
email_created_path = base_path+'created_emails'

scrapper_output = base_path + 'automatic_emails_format_created'
missing_data = base_path+'missing_emails'
verified_path = base_path+'verified_emails'

track_automation = "track_automation"

dirs_to_create = {
    "source_files": os.path.join(base_path, "database_source_files"),
    "output_files": os.path.join(base_path, "database_output_files"),
    "main_db": os.path.join(base_path, "main_database"),
    "created_emails": os.path.join(base_path, "created_emails"),
    "scraper_output": os.path.join(base_path, "automatic_emails_format_created"),
    "missing_data": os.path.join(base_path, "missing_emails"),
    "verified": os.path.join(base_path, "verified_emails"),
    "track_automation" : "track_automation"
}

# Create all directories if they don't exist
for name, path in dirs_to_create.items():
    os.makedirs(path, exist_ok=True)


# Data to initialize if files are missing
new_data = {'10th sfg': 'LastName@soc.mil'}

# Helper function to safely create pickle file if it doesn't exist
def create_pickle_if_missing(file_path, data):
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
# Check and create both files
create_pickle_if_missing(new_db_pickle_file_path, new_data)
create_pickle_if_missing(old_db_pickle_file_path, new_data)


@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received request...")
    log_message = "Tool"

    if 'file' not in request.files:
        print("Error: No file in request")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file:
        print("Processing single file...")

        # Ensure UPLOAD_FOLDER exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        print(f"File saved at: {file_path}")

        try:
            process_single_file(file_path, Output_files_path,old_db_pickle_file_path)
            
            log_message = "File processed successfully!"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        

    
    if 'folder' in request.files:

        print ("folder is selected")
        
        files = request.files.getlist('folder')  # Get all files in the folder
        filenames = [file.filename for file in files if file.filename != '']
        for i in filenames:
            print ("filenames ",i)
            try:
                if i.endswith('.csv') or i.endswith('.xlsx'):
                    file_path = f"{base_path}//{i}"

                    process_single_file(file_path, Output_files_path,old_db_pickle_file_path)

            except Exception as e:
                log_message = f"Error processing file: {str(e)}"
      
        log_message = "File processed successfully!"

        return jsonify({"log": log_message})




@app.route('/update-database-manually', methods=['POST'])
def update_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']


    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            # data = pd.read_excel(file_path) if file.filename.endswith('.xlsx') else pd.read_csv(file_path)

            updated_dictd = update_pickle(new_db_pickle_file_path, file_path)
            from pathlib import Path
            import csv
            file_paths = Path(new_db_pickle_file_path)
            folder_path = file_paths.parent
            #create csv out of dictionary
            if isinstance(updated_dictd, dict):
                # Write to CSV with UTF-8 encoding
                print (folder_path / "new_database.csv")
                with open(folder_path / "new_database.csv", "w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["Key", "Value"])  # Header
                    for key, value in updated_dictd.items():
                        writer.writerow([key, value])
            updated_dict = update_pickle(old_db_pickle_file_path, file_path)
        
            if isinstance(updated_dict, dict):
                # Write to CSV with UTF-8 encoding
                print (folder_path / "old_database.csv")
                with open(folder_path / "old_database.csv", "w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["Key", "Value"])  # Header
                    for key, value in updated_dict.items():
                        writer.writerow([key, value])

            log_message = "File processed successfully! Rows:, Columns:"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"
        return jsonify({"log": log_message})


    if 'folder' in request.files:

        print ("folder is selected")
        
        files = request.files.getlist('folder')  # Get all files in the folder
        filenames = [file.filename for file in files if file.filename != '']
        for i in filenames:
            print ("filenames ",i)
            try:
                if i.endswith('.csv') or i.endswith('.xlsx'):
                    file_path = f"{base_path}//{i}"

                    updated_dict = update_pickle(new_db_pickle_file_path, file_path)
                    updated_dict = update_pickle(old_db_pickle_file_path, file_path)

                    log_message = "File processed successfully! Rows:, Columns:"
                    log_message = "File processed successfully!"
            except Exception as e:
                log_message = f"Error processing file: {str(e)}"
        print("log", log_message)
    

        return jsonify({"log": log_message})





'''
-------------------------------------------------------------Email-------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''

@app.route('/email', methods=['POST'])
def create_email():

    # Load the pickle file
    with open(new_db_pickle_file_path, 'rb') as f:
        email_patterns = pickle.load(f)

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    if 'folder' in request.files:

        print ("folder is selected")
        
        files = request.files.getlist('folder')  # Get all files in the folder
        filenames = [file.filename for file in files if file.filename != '']
        combined_email_data = pd.DataFrame()
        for i in filenames:
            print ("filenames ",i)

            try:
                if i.endswith('.csv') or i.endswith('.xlsx'):
                    dir_file = f"{base_path}/{i}"
                    print (f"file names {dir_file}")
                    df = email_creator_app(dir_file,email_patterns)

                    missing = df[df["Email"].isna() | (df["Email"].str.strip() == "")]

                    email_data = df[df["Email"].notna() & (df["Email"].str.strip() != "")]

                    combined_email_data = pd.concat([combined_email_data, email_data], ignore_index=True)

                                        # Get file name without extension
                    file_name_no_ext = os.path.splitext(os.path.basename(i))[0]

                    filename_csv = f"{email_created_path}//{file_name_no_ext}_new_tool_output.csv"

                    email_data.to_csv(filename_csv)
                    missing_file_name =   f"{missing_data}//{file_name_no_ext}_new_tool_missing.csv"
                    missing.to_csv(missing_file_name)
                    rows, columns = df.shape
                    log_message = f"File processed successfully! Rows: {rows}, Columns: {columns}"


                   
            except Exception as e:
             print(f"Error processing {i}: {str(e)}")

                # Save the final combined DataFrames after the loop
        final_email_file = f"{email_created_path}/combined_email_output.csv"

        combined_email_data.to_csv(final_email_file, index=False)


    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        print ("file is selected")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the file
        try:

            df = email_creator_app(file_path,email_patterns)
            
            missing = df[df["Email"].isna() | (df["Email"].str.strip() == "")]

            email_data = df[df["Email"].notna() & (df["Email"].str.strip() != "")]

                                # Get file name without extension
            file_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]

            filename_csv = f"{email_created_path}//{file_name_no_ext}_new_tool_output.csv"

            email_data.to_csv(filename_csv)
            missing_file_name =   f"{missing_data}//{file_name_no_ext}__new_tool_missing.csv"
            missing.to_csv(missing_file_name)
            rows, columns = df.shape
            log_message = f"File processed successfully! Rows: {rows}, Columns: {columns}"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        return jsonify({"log": log_message})


'''
--------------------------------------------------------------Verify-------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''

@app.route('/email-verify', methods=['POST'])
def verify_email():

    # Load the pickle file
    with open(old_db_pickle_file_path, 'rb') as f:
        email_patterns = pickle.load(f)

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400


    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the file
        try:
                                            # Get file name without extension
            api_key = '748ad80421514463bb9099b85004b0dd'
            url = 'https://api.zerobounce.net/v2/validate'
            df= verify_app(file_path, api_key)
            file_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]

            filename_csv = f"{verified_path}//{file_name_no_ext}_Verified.csv"

            df.to_csv(filename_csv)

            rows, columns = df.shape
            log_message = f"File processed successfully! Rows: {rows}, Columns: {columns}"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        return jsonify({"log": log_message})


'''
--------------------------------------------------------automatic email formats------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''


import time
from datetime import datetime, timedelta

def log_query_result(log_file, query, results, error=None):
    """Logs each query with its results or errors in a persistent text file."""
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if error:
            log_entry = f"{timestamp} | QUERY: {query} | ERROR: {error}\n"
        else:
            log_entry = f"{timestamp} | QUERY: {query} | RESULTS: {results}\n"

        f.write(log_entry)
        f.flush()  # Ensure data is written immediately





@app.route('/automatic-email', methods=['POST'])

def automatic_email():


    # Load the pickle file
    with open(new_db_pickle_file_path, 'rb') as f:
        email_patterns = pickle.load(f)


    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        output_txt_file = "track_automation//"+file_name + ".txt"
        output_txt_file = output_txt_file.replace(" ","")

        checkpoint_file = "track_automation//"+file_name+"checkpoint.txt"
        checkpoint_file = checkpoint_file.replace(" ","")

        # create text file from missing data with conpany name and index
        df = pd.read_csv(file_path)

        unique_companies = df["Company"].dropna().unique()  # Assuming 'company_name' is the column name
       
        # Write unique company names to the output text file with index
        with open(output_txt_file, "w") as f:
            for i, company in enumerate(unique_companies, start=0):
                f.write(f"{i} {company}\n")

        with open(output_txt_file, "r" ) as file:
            company_list = [line.strip().split(maxsplit=1)[1] for line in file if line.strip()]


        # Determine the starting index from the checkpoint file
        if os.path.exists(checkpoint_file):

            with open(checkpoint_file, "r") as f:
                last_index, last_file = f.readline().strip().split()
                last_index = int(last_index)
        else:
            last_index = 0
            with open(checkpoint_file, "w") as f:
                f.write(f"{last_index} {output_txt_file}\n")
        
        # Define batch size
        BATCH_SIZE  = 20000 # file size
        batch_row = 10000 # first batch in outer circle 
        batch_sizes = 98 # batch inside circle

        queries = company_list[last_index:last_index+BATCH_SIZE]
        # Get the number of full batches
        num_batches = len(queries) // batch_row  # Number of complete batches
        remainder = len(queries) % BATCH_SIZE  # Remaining elements in an extra batch (if any)
        # Iterate over batches
        start = 0
        total_rows = 0
        for batch_idx in range(num_batches + (1 if remainder > 0 else 0)):  # Include remainder batch
            start_index = batch_idx * batch_row
            end_index = min(start_index + batch_row, len(queries))  # Avoid exceeding list size
            batch = queries[start_index:end_index]

            

            print ("\n", f"**************************  Batch:: {start_index}_{end_index}  *********************************")
            print (f"starting from {last_index} row")

            # Print batch details
            namefile = f"{scrapper_output}/Batch_{start_index}_{end_index}_google_"
            df_raw=0
            df_raw= scrapper_manager(queries[start_index:end_index],namefile, last_index, output_txt_file,old_db_pickle_file_path,new_db_pickle_file_path,checkpoint_file,batch_sizes) 
            time.sleep(30)
            start = start+int(df_raw)
            total_rows =  batch_row*  (batch_idx+1)
            last_index= last_index+BATCH_SIZE
            socketio.emit("log_update", {"logs": f"Total results: {start}/{total_rows}"})  # Send logs

# create emails

            print (f"{total_rows} rows completed")

            df = email_creator_app(file_path,email_patterns)
            print ("emails created")

            email_data = df[df["Email"].notna() & (df["Email"].str.strip() != "")]

                                # Get file name without extension
            file_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]

            filename_csv = f"{scrapper_output}//{file_name_no_ext}_generated_emails_output.csv"

            email_data.to_csv(filename_csv)

    log_message = f"File processed successfully!"
    print (log_message)
         
    return jsonify({"log": log_message})






'''
--------------------------------------------------------Split File------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''

@app.route('/split-file', methods=['POST'])
def split_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Read the file and print first 5 rows
        try:
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)

            print(df.head())  # Print first 5 rows

            log_message = f"File uploaded successfully! Showing first 5 rows:\n{df.head().to_string()}"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        return jsonify({"log": log_message})







@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    # Clear log functionality (optional if needed)
    return jsonify({"log": "Logs cleared!"})

if __name__ == '__main__':
    app.run(host ='new-tool', port=3000, debug=True)
