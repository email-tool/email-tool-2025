import requests
from bs4 import BeautifulSoup
import math
# from duckduckgo_search import DDGS
import time


# https://www.startpage.com/
# Fetch Bing results
def fetch_startpage_results(query, num_results=5):
    language = 'en'
    url = f"https://www.startpage.com/search?q={query}&setlang={language}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for item in soup.find_all('li', class_='b_algo')[:num_results]:
        title = item.find('h2')
        link = title.find('a')['href'] if title else None
        snippet = item.find('p').text if item.find('p') else None
        if title and link:
            results.append({'title': title.text, 'link': link, 'snippet': snippet})
    # If no results are found, return a single entry with "NA" values
    if not results:
        results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
    return results



# Fetch Bing results
def fetch_bing_results(query, num_results=10):
    language = 'en'
    # url = f"https://www.bing.com/search?÷q={query}&setlang={language}"
    url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for item in soup.find_all('li', class_='b_algo')[:num_results]:
        title = item.find('h2')
        link = title.find('a')['href'] if title else None
        snippet = item.find('p').text if item.find('p') else None
        if title and link:
            results.append({'title': title.text, 'link': link, 'snippet': snippet})
    # If no results are found, return a single entry with "NA" values
    if not results:
        results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
    return results

# Fetch Yahoo results
def fetch_yahoo_results(query, num_results=30):
    url = f"https://search.yahoo.com/search?p={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for item in soup.find_all('div', class_='Sr')[:num_results]:
        title = item.find('h3')
        link = item.find('a')['href'] if item.find('a') else None
        snippet = item.find('p').text if item.find('p') else None
        if title and link:
            results.append({'title': title.text, 'link': link, 'snippet': snippet})
    # If no results are found, return a single entry with "NA" values
    if not results:
        results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
    return results


import requests
from bs4 import BeautifulSoup
from googlesearch import search


def fetch_google_results(query, num_results=5):

    results = list(search(query, num_results=5, advanced= True) ) # Fetch up to 4 results
    data=[]
    for i, result in enumerate(results, start=5):

        data.append({'title': result.title, 'link': result.url, 'snippet': result.description})
    return data

    # If no results are found, return a single entry with "NA" values
    if not results:
        results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
        
    return results




# Fetch DuckDuckGo results
# def fetch_duckduckgo_results(query, num_results=5):
#     resultss = DDGS().text(query, max_results=num_results)
#     # Transform the data into the desired format
#     formatted_data = [
#         {
#             'title': item['title'],
#             'link': item['href'],
#             'snippet': item['body']
#         }
#         for item in resultss
#     ]
#     results = []

#     if not formatted_data:
#         results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
#     else:
#         for i in range(len(formatted_data)): 
#             results.append({'title': formatted_data[i]["title"], 'link': formatted_data[i]["link"], 'snippet': formatted_data[i]["snippet"]})
    
#     return results



# Function to handle retries if an engine fails
def fetch_results_with_retry(query, num_results=5, engines=["DuckDuckGo", "Bing", "Yahoo"]):
    for engine in engines:
        try:
            if engine == "DuckDuckGo":
                return fetch_duckduckgo_results(query, num_results)
            elif engine == "Bing":
                return fetch_bing_results(query, num_results)
            elif engine == "Yahoo":
                return fetch_yahoo_results(query, num_results)
        except Exception as e:
            print(f"Failed to fetch results from {engine} for query '{query}': {e}")
    # If all engines fail, return a result with "NA"
    return [{'title': 'error', 'link': 'error', 'snippet': 'error'}]

# Function to distribute queries across batches
def distribute_queries_across_engines(queries, batch_size):
    search_engines = [ "Bing", "Yahoo"]
    
    num_batches = math.ceil(len(queries) / batch_size)
    all_results = []

    start_time = time.time()  # Start time for entire execution
    print ("Number of batch:", num_batches, " and each batch have ", batch_size, " many rows ")
    for batch_idx in range(num_batches):
        # Start time for this batch
        batch_start_time = time.time()

        # Get queries for the current batch
        start_idx = batch_idx * batch_size
        end_idx = start_idx + batch_size
        current_queries = queries[start_idx:end_idx]
        
        print(f"\nFetching batch {batch_idx + 1}...")

        for query in current_queries:
            try:
                # Try fetching results with retries
                results = fetch_results_with_retry(query, num_results=5)
                # Ensure that we always have at least one result entry for each engine
                if not results:  # If results are empty, append a result with "NA"
                    results.append({'title': 'NA', 'link': 'NA', 'snippet': 'NA'})
                all_results.append({'query': query, 'engine': "Retry", 'results': results})
            except Exception as e:
                print(f"Failed to fetch results for query '{query}': {e}")
                # In case of error, we append the result with "NA" values for this query
                all_results.append({'query': query, 'engine': "Retry", 'results': [{'title': 'error', 'link': 'error', 'snippet': 'error'}]})

        # End time for this batch
        batch_end_time = time.time()
        batch_duration = batch_end_time - batch_start_time
        print(f"Batch {batch_idx + 1} completed in {batch_duration:.2f} seconds.")
        
        # Delay of 1 minute after each batch
        print("Waiting for 1 minute before starting the next batch...")
        time.sleep(3)  # Wait for 60 seconds (1 minute)

    # End time for entire execution
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"\nTotal execution time: {total_duration:.2f} seconds.")
    
    return all_results





def get_email_from_snippet(data):
    import pandas as pd
    import re
    from urllib.parse import urlparse
    # Function to extract domain name from URL
    def extract_website(url):
        domain = urlparse(url).netloc
        return domain.split('.')[0] if domain else "Unknown"

    # Function to extract email format from snippet
    def extract_email(snippet):
        match = re.search(r'[\w\.\[\]]+@[\w\.\[\]]+', snippet)  # Extracts email-like patterns
        return match.group(0) if match else "Not Found"

    # Function to extract accuracy from snippet (if mentioned)
    def extract_accuracy(snippet):
        match = re.search(r'(\d{1,3}\.\d+)%', snippet)
        return float(match.group(1)) if match else "Unknown"

    # Creating DataFrame
    records = []
    for entry in data:
        for result in entry['results']:
            text = (entry['query'])
            # Extract text after "email format for"
            company = text.replace("email format for", "").strip()
            website = extract_website(result['link'])
            email = extract_email(result['snippet'])
            accuracy = extract_accuracy(result['snippet'])
            query = company
            records.append({"Company":query,"Website": website, "Email": email, "Accuracy": accuracy})

    df = pd.DataFrame(records)

    # Display DataFrame
    return df
