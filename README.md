# Web Crawler & Searcher Project

## Table of Contents

- [Web Crawler \& Searcher Project](#web-crawler--searcher-project)
  - [Table of Contents](#table-of-contents)
  - [Project Title](#project-title)
  - [Description](#description)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Screenshots](#screenshots)
  - [Example Output](#example-output)
  - [File Structure](#file-structure)
  - [License](#license)

## Project Title

**Web Crawler & Searcher Project**

## Description

This Python-based application is designed to crawl web pages and perform search queries using configurable parameters. It leverages a configuration file (*config.ini*) to set settings such as the target URL, user agent, and HTTP headers. The project is split into modular components that handle crawling, searching, and configuration management.

**Key Features:**
- **Web Crawling:** Automatically fetch and parse web content.
- **Configurable Search:** Adjust settings like the search URL and HTTP headers via *config.ini*.
- **Output Generation:** Search results are saved as CSV files for easy viewing and further processing.
- **Learning Experience:** Gain insights into Python module design, configuration handling, and HTTP requests.

## Installation

1. **Prerequisites:**
   - Python 3.6 or later.
   - Active internet connection for web crawling.

2. **Setup Instructions:**
   - Clone the repository to your local machine.
   - Open a terminal and navigate to the project directory.
   - *(Optional)* Create and activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate    # On Windows: venv\Scripts\activate
     ```
   - Install the required dependencies. If a `requirements.txt` file is provided, run:
     ```bash
     pip install -r requirements.txt
     ```
   - Otherwise, ensure that libraries such as `requests` are installed.

## Usage

To run the application, use the main script:
```bash
python main.py
```
The program will:
1. Load the initial page (from the URL specified in *config.ini*).
2. Prompt you to enter a search keyword (e.g., **weizenmehl**).
3. Crawl the search results and extract company data.
4. Save the data in a CSV file (e.g., **company_details.csv**).

### Screenshots

- **page_loaded.png**: Shows the initial landing page on [wlw.de](https://www.wlw.de/) before any search is performed, including the cookie acceptance banner.  
- **after_search_submit.png**: Demonstrates the search results page after entering the keyword **“weizenmehl”**, showing matching companies and brief details.

## Example Output

After entering the keyword **weizenmehl**, the application produces a CSV file named **company_details.csv**. This file typically includes:

- **Company Name**
- **Website URL**
- **Address**
- **Additional Contact or Business Details**

## File Structure

- **main.py**: The main entry point that orchestrates the crawling and searching operations.
- **searcher.py**: Contains the functionality to perform search queries.
- **crawler.py**: Implements the logic for crawling web pages.
- **config.ini**: Stores configuration settings such as the search URL and HTTP header information. For example, the file includes:
  - `search_url` set to *https://www.wlw.de/*
  - A custom `user_agent` and various HTTP headers  
- **config_handler.py**: Manages loading and parsing configuration settings from *config.ini*.
- **company_details.csv**: The output file generated after running a search query (e.g., when searching for **weizenmehl**).

## License

This project is licensed under the MIT License. See the LICENSE file for more details.