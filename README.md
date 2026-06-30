# bing-copilot-citation-mapper
A Python script to extract, map, and analyze internal URL data for Bing AI/Copilot grounding queries from Bing Webmaster Tools.

# Bing Copilot AI Citation Mapper

An automated Python script designed to bypass UI limits in Bing Webmaster Tools and programmatically map "Grounding Queries" (AI Search Queries) directly to the specific internal URLs Bing uses to cite your brand.

## Why This Tool Exists
Bing Webmaster Tools provides incredibly valuable insights into how Bing Copilot cites your website. However, the online UI forces you to click into every single query individually to see which page is being cited. 

If you have thousands of queries, this takes days. This script automates the internal API endpoints to scrape, map, and compile all queries and their corresponding pages into a single, clean `.csv` dataset.

## Features
- **Dynamic Key Adaptability:** Automatically handles Bing API structural formats (`Queries` vs `Data`).
- **Resilient Error Handling:** Gracefully navigates standard Bing server responses (`404 NoDataFound` and `503 Service Unavailable`) without crashing the execution loop.
- **Smart Rate Limiting:** Includes built-in micro-pauses and automated 5-minute timeout cooldowns to manage Bing's `429 Too Many Requests` thresholds.
- **Credential Security:** Reads session values safely out of a local `env.txt` file, ensuring you never commit live browser cookies to GitHub.

## Prerequisites
- Python 3.x
- Jupyter Notebook
- `pandas` and `requests` libraries
