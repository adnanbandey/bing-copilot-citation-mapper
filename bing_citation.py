import requests
import pandas as pd
import time
import copy
import os
from dotenv import load_dotenv

# ==========================================
# CONFIGURATION
# ==========================================

# Initialize variables
COOKIE_STRING = ""
CSRF_TOKEN = ""

# Read from your local text file 
with open("env.txt", "r") as f:
    for line in f:
        if line.startswith("BING_COOKIE="):
            COOKIE_STRING = line.replace("BING_COOKIE=", "").strip()
        elif line.startswith("BING_CSRF="):
            CSRF_TOKEN = line.replace("BING_CSRF=", "").strip()

# Quick sanity check
if COOKIE_STRING and CSRF_TOKEN:
    print("Credentials loaded successfully from file!")
else:
    print("Error: Could not find credentials. Check your file formatting.")



# Load the keys from the hidden file
# load_dotenv()

# COOKIE_STRING = os.getenv("BING_COOKIE")
# CSRF_TOKEN = os.getenv("BING_CSRF")

PAYLOAD_TEMPLATE = {
    "SiteUrl": SITE_URL,
    "AIFilterKeyword": "",
    "DateRange": {
        "BeginTimeStamp": "Mon, 29 Dec 2025 00:00:00 GMT",
        "EndTimeStamp": "Sun, 28 Jun 2026 00:00:00 GMT"
    },
    "Page": "",
    "Pagination": {
        "PageNum": 1,
        "PageSize": 100
    },
    "Query": "",
    "SortParameters": {
        "SortField": "Citations",
        "SortOrder": "Desc"
    }
}

BASE_URL = "https://www.bing.com/webmasters/api/aiperformance"
QUERIES_ENDPOINT = f"{BASE_URL}/searchqueries/stats"
PAGES_ENDPOINT = f"{BASE_URL}/pages/stats"

HEADERS = {
    "Cookie": COOKIE_STRING,
    "x-csrf-token": CSRF_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    # Add these two lines to bypass the 400 error:
    "Origin": "https://www.bing.com",
    "Referer": "https://www.bing.com/webmasters/"
}

def make_api_request(endpoint, payload):
    """Makes a request to Bing APIs and handles rate limiting (429 Too Many Requests)."""
    while True:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Bing rate limit hit (429). Waiting 5 minutes...")
            time.sleep(300) # Wait 5 minutes
        elif response.status_code in [401, 403]:
            raise Exception(f"Auth Error {response.status_code}: Your cookie or token has expired.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

def get_all_queries():
    """Fetches all grounding queries using the updated 'Queries' key."""
    all_queries = []
    page_num = 1
    
    print("Fetching all grounding queries...")
    while True:
        payload = copy.deepcopy(PAYLOAD_TEMPLATE)
        payload["Pagination"]["PageNum"] = page_num
        
        data = make_api_request(QUERIES_ENDPOINT, payload)
        
        # FIX: Look for "Queries" instead of "Data"
        if not data or not data.get("Queries"):
            break
            
        queries = data["Queries"]
        all_queries.extend(queries)
        print(f"Fetched {len(all_queries)} queries so far...")
        
        if len(queries) < payload["Pagination"]["PageSize"]:
            break
            
        page_num += 1
        
    return all_queries

queries = get_all_queries()
print(f"Total queries found: {len(queries)}")

print("Mapping pages to queries. This will take some time...")
mappings = [] 

for index, query_data in enumerate(queries):
    # FIX: Extract using "GroundingQuery" based on your diagnostic printout
    query_text = query_data.get("GroundingQuery")
    if not query_text:
        continue
    
    if index > 0 and index % 150 == 0:
        print("Preemptive cooldown to avoid rate limit. Waiting 45 seconds...")
        time.sleep(45)
        
    page_payload = copy.deepcopy(PAYLOAD_TEMPLATE)
    page_payload["Query"] = query_text 
    
    pages_data = make_api_request(PAGES_ENDPOINT, page_payload)
    
    if pages_data:
        # Adaptive check: looks for 'Pages', 'Urls', or 'Data' fields dynamically
        pages_list = pages_data.get("Pages") or pages_data.get("Urls") or pages_data.get("Data") or []
        
        for page in pages_list:
            # Safely grab url and citations checking common naming patterns
            url = page.get("Url") or page.get("PageUrl") or page.get("Page")
            citations = page.get("Citations", 0)
            
            if url:
                mappings.append({
                    "Query": query_text,
                    "Query_Citations": query_data.get("Citations", 0),
                    "Page_URL": url,
                    "Mapped_Citations": citations
                })
    
    if index > 0 and index % 10 == 0:
        print(f"Processed {index}/{len(queries)} queries...")

print("Finished processing all queries!")


# 3. Load into a pandas DataFrame and Export to CSV
if mappings:
    df = pd.DataFrame(mappings)
    
    # Display the first 5 rows in the notebook
    display(df.head())
    
    # Export to file
    df.to_csv("bing_ai_mapping.csv", index=False)
    print("\nSuccess! Exported complete mapping to bing_ai_mapping.csv")
else:
    print("\nNo mappings were found.")
