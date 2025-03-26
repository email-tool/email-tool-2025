import pandas as pd
from automatic_email_format.web_email_scrapper_multiEngine import fetch_yahoo_results,fetch_google_results
import time, math, random
from datetime import datetime, timedelta

import pandas as pd
import re, os,pickle
from urllib.parse import urlparse

from automatic_email_format.get_email_flags import get_flags

# Function to identify email format
def get_email_pattern(email):
    if not isinstance(email, str) or "@" not in email:
        return "NA"


    # print ("*"*80)
    email_prefix = email.split("@")[0].strip().lower()
    try:
        domain = email.split("@")[1].strip().lower()
    except:
        domain = "NA"
    # print (email_prefix)
    email_prefix = email_prefix.replace(" '.' ", ".").replace(" '-' ", "-").replace(" '_' ", "_").replace('first_initial', 'f').replace('last_initial', 'l').replace("filast","flast")
    email_prefix = email_prefix.replace(" ", "")
    # print (email_prefix)
    # print ("*"*80,"\n")
    # Remove spaces and normalize format
    email_prefix = re.sub(r"\s+", "", email_prefix)

    # Define name variations
    names = [
        {"first": "john", "last": "smith"},
        {"first": "john", "last": "doe"},
        {"first": "jane", "last": "doe"},
        {"first": "first", "last": "last"},
        {"first": "fir", "last": "last"},
        {"first": "firstname", "last": "lastname"},
        {"first": "john", "last": "doe","middle_name":"michael"}

    ]

    for name in names:
        first_name = name["first"]
        last_name = name["last"]
        try:
            middle_name = name['middle_name']
        except:
            middle_name = ""
            patterns = {
    "FirstName": first_name,
    "LastName": last_name,

    "FirstInitial": f"{first_name[0]}", 
    "LastInitial": f"{last_name[0]}", 

    "FirstName.LastName": f"{first_name}.{last_name}",
    "FirstName_LastName": f"{first_name}_{last_name}",
    "FirstName-LastName": f"{first_name}-{last_name}",
    "FirstNameLastName": f"{first_name}{last_name}",

    "LastName.FirstName": f"{last_name}.{first_name}",
    "LastName_FirstName": f"{last_name}_{first_name}",
    "LastName-FirstName": f"{last_name}-{first_name}",
    "LastNameFirstName": f"{last_name}{first_name}",

    "FirstInitialLastName": f"{first_name[0]}{last_name}",
    "FirstInitial.LastName": f"{first_name[0]}.{last_name}",
    "FirstInitial_LastName": f"{first_name[0]}_{last_name}",
    "FirstInitial-LastName": f"{first_name[0]}-{last_name}",

    "FirstInitialLastInitial": f"{first_name[0]}{last_name[0]}",
    "FirstInitial.LastInitial": f"{first_name[0]}.{last_name[0]}",
    "FirstInitial_LastInitial": f"{first_name[0]}_{last_name[0]}",
    "FirstInitial-LastInitial": f"{first_name[0]}-{last_name[0]}",

    "FirstName.LastInitial": f"{first_name}.{last_name[0]}",
    "FirstName_LastInitial": f"{first_name}_{last_name[0]}",
    "FirstName-LastInitial": f"{first_name}-{last_name[0]}",
    "FirstNameLastInitial": f"{first_name}{last_name[0]}",

    "LastName.FirstInitial": f"{last_name}.{first_name[0]}",
    "LastName_FirstInitial": f"{last_name}_{first_name[0]}",
    "LastName-FirstInitial": f"{last_name}-{first_name[0]}",
    "LastNameFirstInitial": f"{last_name}{first_name[0]}",

    "FirstInitialLastNameLastInitial": f"{first_name[0]}{last_name}{last_name[0]}",  # Fixed from FirstInitialLastName1
    "FirstInitialLastName": f"{first_name[0]}{last_name}",  # Fixed from FirstName1LastName
    "FirstNameLastInitial": f"{first_name}{last_name[0]}",  # Fixed from FirstNameLastName1
    "LastInitialFirstName": f"{last_name[0]}{first_name}",  # Fixed from LastName1FirstName
    "LastNameFirstInitial": f"{last_name}{first_name[0]}",  # Fixed from LastNameFirstName1

    "LastInitial.FirstInitial": f"{last_name[0]}.{first_name[0]}",
    "LastInitial-FirstInitial": f"{last_name[0]}-{first_name[0]}",
    "LastInitial_FirstInitial": f"{last_name[0]}_{first_name[0]}",
    "LastInitialFirstInitial": f"{last_name[0]}{first_name[0]}",

    "LastInitial.FirstName": f"{last_name[0]}.{first_name}",
    "LastInitial-FirstName": f"{last_name[0]}-{first_name}",
    "LastInitial_FirstName": f"{last_name[0]}_{first_name}",
    "LastInitialFirstName": f"{last_name[0]}{first_name}",
}


        for pattern_name, pattern in patterns.items():
            if pattern == email_prefix:
                return pattern_name + "@" + domain

    return "Unknown Pattern"

 #Function to extract full email format after "email formats: 1."
def extract_email_format(snippet):
    if not isinstance(snippet, str):
        return []

    pattern = r"email formats:\s*1\.\s*([^()]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    match = re.search(pattern, snippet)

    return [match.group(1).strip()] if match else []

# Function to extract actual email addresses
def extract_emails(snippet):
    if not isinstance(snippet, str):
        return []

    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', snippet)  # Extracts actual emails
    return emails if emails else []
def select_best_row(group):
    for _, row in group.iterrows():
        if row["email pattern"] and row["email pattern"] != ["Unknown Pattern"]:  
            row["email pattern"] = [row["email pattern"][0]]  # Keep only the first pattern
            return row
    return group.iloc[0]  # If no valid email pattern, return the first row

def get_email_patterns_only(yesterday_data, name):
    yesterday_data.columns = yesterday_data.columns.str.lower()
    yesterday_data = yesterday_data[['company', 'snippet']]
    yesterday_data = yesterday_data.drop_duplicates(keep="first").reset_index(drop=True)
    yesterday_data["email_formats_list"] = yesterday_data["snippet"].apply(lambda x: extract_email_format(x) + extract_emails(x))
    yesterday_data["email pattern"] = yesterday_data["email_formats_list"].apply(lambda email_list: [get_email_pattern(email) for email in email_list])
    # Apply the function to each company group
    filtered_df = yesterday_data.groupby("company", group_keys=False).apply(select_best_row)

    # Reset index
    filtered_df.reset_index(drop=True, inplace=True)
    filtered_df["company"] = filtered_df["company"].str.strip()
    filtered_df["email pattern"] = filtered_df["email pattern"].apply(lambda x: x[0] if x else "NA")
    filtered_df= filtered_df[['company', 'email pattern']]

    filtered_df = filtered_df[filtered_df['email pattern'] != 'NA']
    return (filtered_df)


def createCSV(data,name):
    # Creating DataFrame
    records = []
    for entry in data:
        for result in entry['results']:
            text = (entry['query'])
            # Extract text after "email format for"
            company = text.replace("what is email format for ", "").strip()
            company = company.replace("+", " ").strip()
            snippet = result['snippet']
            query = company
            records.append({"Company":query, "Snippet": snippet})

    df = pd.DataFrame(records)

    df = get_email_patterns_only(df, name)
    df = get_flags(df,'email pattern')

    df = df[df['match'].isin(['High', 'Medium'])]

    if df.shape[0] >0:
    
        df.to_csv(name)
    return df

def process_csv(data):

    # Convert all column names to lowercase
    data.columns = data.columns.str.lower()

    # Drop rows where "company" or "email format" are null
    data.dropna(subset=["company", 	"email pattern"], inplace=True)

    # Convert to dictionary
    new_dict = {}
    for _, row in data.iterrows():
        company = row["company"] # Normalize company name to lowercase
        email_format = row["email pattern"]
        new_dict[company] = [email_format]

    return new_dict

# Function to update the pickle file
def update_pickle(pickle_file, new_csv_file):
    print ("update_pickle", pickle_file)
    # Load the existing pickle file
    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as file:
            email_dict = pickle.load(file)
            print ("Shape of old data:", len(email_dict))
    else:
        email_dict = {}

    # Process the new CSV file
    new_data = process_csv(new_csv_file)

    # Update the existing dictionary with new data (replace if company already exists)
    email_dict.update(new_data)
    print ("Shape of new data:", len(email_dict))
    # Save the updated dictionary back to the pickle file
    with open(pickle_file, "wb") as file:
        pickle.dump(email_dict, file)

    print(f"****************Pickle file updated: {pickle_file}")
    return email_dict


def scrapper_manager(queries,name_file, last_index, output_txt_file, db_pickle_file_path):

    dfss = []

    print ("printing lenghth", len(queries))
    search_engines = [fetch_google_results, fetch_yahoo_results]  # Alternating search engines\
    h = ['Google', 'yahoo']
    engine_pt = 0
    batch_size = 2
    num_batches = math.ceil(len(queries) / batch_size)
    all_results = []

    yahoo_downtime = datetime.now() - timedelta(hours=1)
    bing_downtime = datetime.now() - timedelta(hours=1)
    d= datetime.now()

    down_duration = timedelta(minutes=20)  # Yahoo stays down for 1 hour

    start_time = time.time()  # Start time for entire execution
    print ("Number of batch:", num_batches, " and each batch have ", batch_size, " many rows ")
    print (str(datetime.now())[:10])

    for batch_idx in range(num_batches):
        print ("Batch--------------------------------------", batch_idx)

        
        # Start time for this batch
        batch_start_time = time.time()
        # Get queries for the current batch
        start_idx = batch_idx * batch_size
        end_idx = start_idx + batch_size
        current_queries = queries[start_idx:end_idx]

        for query in current_queries:

            company_name = query.replace("what is email format for", "").strip()

            last_index = last_index+1

            print(f"last_index: {last_index}", end="\r")  

            checkpoint_file = "checkpoint.txt"
            with open(checkpoint_file, "w") as f:
                  f.write(f"{last_index} {output_txt_file}\n")

            

            random_number = random.randint(0, 2) + random.random()
            try:
                if engine_pt == 0:
                    if datetime.now() >= yahoo_downtime + down_duration:
                        try :

                            res = search_engines[engine_pt](query , num_results=5)
                            links = [item['link'] for item in res if item.get('link')]

                            q = f"email format for {links[0]}"

                            time.sleep(3)


                            results = search_engines[engine_pt](q, num_results=10)
                        except Exception as e:
                            print(f" Failed to fetch results for query '{query}': {e}") 
                            yahoo_downtime = datetime.now()
    
                        all_results.append({'query': company_name, 'engine': h[engine_pt], 'results': results})
                    else:
                        try :
                            results = search_engines[1-engine_pt](query, num_results=10)
                        except:
                            yahoo_downtime = datetime.now()
                            print(f" Failed to fetch results for query '{query}': {e}") 
                        all_results.append({'query': company_name, 'engine': h[1-engine_pt], 'results': results})

                if engine_pt == 1:

                    if datetime.now() >= bing_downtime + down_duration:
                        try :


                            res = search_engines[engine_pt](query , num_results=5)
                            links = [item['link'] for item in res if item.get('link')]

                            q = f"email format for {links[0]}"

                            time.sleep(3)
                        
                            results = search_engines[engine_pt](q, num_results=10)
                        except:
                            print(f" Failed to fetch results for query '{query}': {e}") 
                            bing_downtime = datetime.now()
                        if not results:  # If results are empty, append a result with "NA"
                            results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
                        all_results.append({'query': company_name, 'engine': h[engine_pt], 'results': results})
                    else:
                        try :
                            results = search_engines[1-engine_pt](query, num_results=10)
                        except:
                            print(f" Failed to fetch results for query '{query}': {e}") 
                            bing_downtime = datetime.now()
                        if not results:  # If results are empty, append a result with "NA"
                            results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
                        all_results.append({'query': company_name, 'engine': h[1-engine_pt], 'results': results})

            except Exception as e:
                print(f"                Failed to fetch results for query '{query}': {e}")  
            time.sleep(random_number)


        engine_pt = 1- engine_pt  
        print (all_results)
        print ("sleeping after batch")
        try:
            df= createCSV(all_results,f"{name_file}_{batch_idx}_{str(datetime.now())[:10]}.csv")

            updated_dict = update_pickle(db_pickle_file_path, f"{name_file}_{batch_idx}_{str(datetime.now())[:10]}.csv")

            print (df)
            print ('createCSV')
            print (f"{name_file}_{batch_idx}_{str(datetime.now())[:10]}.csv")
            # update_pickle(pickle_file, new_csv_file)

            dfss.append(df)  # Append to list
        except Exception as e:
            print(f"Error: {e}")  # Prints the error message
            print ("")
            continue

        time.sleep(1)
    try:
        df_combined = pd.concat(dfss, ignore_index=True)
    except Exception as e:
        print(f"Error: {e}")  # Prints the error message
        print ("")

    return df_combined