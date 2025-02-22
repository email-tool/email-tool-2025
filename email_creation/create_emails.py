import pandas as pd
import pickle
from email_creation.reader_email import reader
# Function to create email based on the pattern
def create_emails(row, email_patterns):
    company_name = row['Company']
    first_name = row['First Name']
    last_name = row['Last Name']

    # Get the email format for the company from the dictionary
    email_pattern = None
    for company, formats in email_patterns.items():
        if company.lower() == company_name.lower():
      
            email_pattern = formats[0].split('@')[0]  # Extract the email pattern before '@'
            domain = formats[0].split('@')[1]
            
            break

    if not email_pattern:
        return None  # Return None if no matching email pattern is found

    # Define patterns for generating emails
    patterns = {
        "FirstName": first_name,
        "LastName": last_name,
        "FirstName.LastName": f"{first_name}.{last_name}",
        "FirstName_LastName": f"{first_name}_{last_name}",
        "LastName.FirstName": f"{last_name}.{first_name}",
        "LastName_FirstName": f"{last_name}_{first_name}",
        "LastName.FirstName1": f"{last_name}.{first_name[0]}",
        "FirstNameLastName": f"{first_name}{last_name}",
        "LastNameFirstName": f"{last_name}{first_name}",
        "FirstName-LastName": f"{first_name}-{last_name}",
        "LastName-FirstName": f"{last_name}-{first_name}",
        "FirstName1LastName": f"{first_name[0]}{last_name}",
        "FirstNameLastName1": f"{first_name}{last_name[0]}",
        "LastName1FirstName": f"{last_name[0]}{first_name}",
        "LastNameFirstName1": f"{last_name}{first_name[0]}",
        "FirstName1.LastName": f"{first_name[0]}.{last_name}",
        "LastName1.FirstName": f"{last_name[0]}.{first_name}",
        "FirstName.LastName1": f"{first_name}.{last_name[0]}",
        "FirstName1_LastName": f"{first_name[0]}_{last_name}",
        "LastName1_FirstName": f"{last_name[0]}_{first_name}",
        "FirstName_LastName1": f"{first_name}_{last_name[0]}"
    }

    # Generate the email based on the pattern
    email_local_part = patterns.get(email_pattern, "")
    if email_local_part:
        email_domain = row['Email'].split('@')[-1]  # Extract domain from the email column
        return f"{email_local_part}@{domain}"
    return None


def email_creator_app(file,email_patterns):
    processed_data= reader(file)
    processed_data['Email'] = ""
    # Apply the email creation function to the dataframe
    processed_data['Email'] = processed_data.apply(create_emails, axis=1, email_patterns=email_patterns)
    return processed_data