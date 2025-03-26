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
from database_training.merger_for_pckl import update_pkl_with_csv
import pandas as pd
from database_training.update_db_manually import update_pickle
from email_creation.create_emails import email_creator_app


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

base_path = r'E:/EmailTool-V2/Barzaan/email_creator_app/files/'


Source_file_path = base_path+'database_source_files'
Output_files_path = base_path+'database_output_files'
db_pickle_file_path = base_path+'main_database//'+'email_patterns.pkl'
email_created_path = base_path+'created_emails'
verified_path = base_path+'verified_emails'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    # Check if a folder is uploaded
    if 'folder' in request.files:
        
        files = request.files.getlist('folder')  # Get all files in the folder
        filenames = [file.filename for file in files if file.filename != '']
        first_file_path = files[0].filename
        folder_name = first_file_path.split('/')[0]  
        print (folder_name)
        process_files_and_save_output(folder_name, Output_files_path)

        process_files_and_save_output(folder_name, Output_files_path)
        update_pkl_with_csv(Output_files_path, db_pickle_file_path)


    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            data = pd.read_excel(file_path) if file.filename.endswith('.xlsx') else pd.read_csv(file_path)
            print ("just one file")
            print (data.head())
            rows, columns = data.shape
            log_message = f"File processed successfully! Rows: {rows}, Columns: {columns}"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        return jsonify({"log": log_message})




@app.route('/update-database-manually', methods=['POST'])
def update_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            # data = pd.read_excel(file_path) if file.filename.endswith('.xlsx') else pd.read_csv(file_path)

            updated_dict = update_pickle(db_pickle_file_path, file_path)

            log_message = f"File processed successfully! Rows:, Columns:"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        return jsonify({"log": log_message})





'''
-------------------------------------------------------------Email-------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------
'''

@app.route('/email', methods=['POST'])
def create_email():

    # Load the pickle file
    with open(db_pickle_file_path, 'rb') as f:
        email_patterns = pickle.load(f)

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    if 'folder' in request.files:
        
        files = request.files.getlist('folder')  # Get all files in the folder
        filenames = [file.filename for file in files if file.filename != '']
        for i in filenames:
            print ("filenames ",i)

            try:
                if i.endswith('.csv') or i.endswith('.xlsx'):
                    df = email_creator_app(i,email_patterns)

                                        # Get file name without extension
                    file_name_no_ext = os.path.splitext(os.path.basename(i))[0]

                    filename_csv = f"{email_created_path}//{file_name_no_ext}_output.csv"

                    df.to_csv(filename_csv)
                    print (df.head(4))
            except Exception as e:
             print(f"Error processing {i}: {str(e)}")
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the file
        try:

            df = email_creator_app(file_path,email_patterns)
                                            # Get file name without extension
            file_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]

            filename_csv = f"{email_created_path}//{file_name_no_ext}_output.csv"
            
            df.to_csv(filename_csv)

            print (df.head(4))
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
    with open(db_pickle_file_path, 'rb') as f:
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
@app.route('/automatic-email', methods=['POST'])
def automatic_email():

    # Load the pickle file
    with open(db_pickle_file_path, 'rb') as f:
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
            print (file_path)
            log_message = f"File processed successfully! Rows: {file_path}"
        except Exception as e:
            log_message = f"Error processing file: {str(e)}"

        return jsonify({"log": log_message})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    # Clear log functionality (optional if needed)
    return jsonify({"log": "Logs cleared!"})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
