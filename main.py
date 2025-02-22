# main.py
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from searcher import Searcher

def save_to_csv(data, filename="company_details.csv"):
    """
    Saves extracted company details to a CSV file.
    """
    try:
        fieldnames = ["Company Name", "Link", "Official Website", "Phone", "Address"]
        with open(filename, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"[INFO] Results saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save results to CSV: {e}")

def main():
    keyword = input("Enter the keyword to search: ").strip()
    print("[DEBUG] Initializing WebDriver...")

    # Create ChromeOptions (headless, images disabled)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # disable images
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    try:
        url = "https://www.wlw.de/"
        driver.get(url)
        print(f"[DEBUG] Navigated to {url}")
        time.sleep(2)  # short wait for page load

        # Create Searcher
        searcher = Searcher(driver)
        if searcher.perform_search(keyword):
            # Parallel detail scraping with 5 threads
            searcher.scrape_company_details_in_parallel(max_workers=5)
            if searcher.results:
                save_to_csv(searcher.results)
            else:
                print("[INFO] No results to save.")
        else:
            print("[INFO] No results found or an error occurred during the search.")

    except Exception as e:
        print(f"[ERROR] Unexpected error in main: {e}")
    finally:
        driver.quit()
        print("[DEBUG] WebDriver closed.")

if __name__ == "__main__":
    main()
