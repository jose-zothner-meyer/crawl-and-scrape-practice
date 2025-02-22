# searcher.py
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Searcher:
    def __init__(self, driver):
        self.driver = driver
        self.results = []  # Will store company details (name, link, etc.)

    def perform_search(self, keyword):
        """
        Use short wait times (2s) to speed up. If the site loads slower, increase these.
        """
        try:
            search_input = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.input"))
            )
            print("[DEBUG] Search input found.")

            search_input.click()
            print("[DEBUG] Search input clicked.")
            time.sleep(1)  # short sleep
            search_input.clear()
            print("[DEBUG] Search input cleared.")

            search_input.send_keys(keyword)
            print(f"[DEBUG] Search keyword '{keyword}' entered.")
            current_value = self.driver.execute_script("return arguments[0].value;", search_input)
            print(f"[DEBUG] Current search input value: '{current_value}'")

            if current_value != keyword:
                print("[ERROR] Search input value does not match the expected keyword.")
                return False

            search_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.submit-button"))
            )
            search_button.click()
            print("[DEBUG] Search button clicked.")

            # Wait until title or URL reflects the search
            WebDriverWait(self.driver, 2).until(
                lambda drv: keyword.lower() in drv.title.lower() or "suche" in drv.current_url
            )
            print("[DEBUG] Page title or URL updated after search.")

            self.driver.save_screenshot("after_search_submit.png")
            print("[DEBUG] Screenshot taken: after_search_submit.png")

            if self.check_no_results():
                print("[DEBUG] No results found on the search page.")
                return False

            self.extract_results_with_pagination()
            return True

        except TimeoutException as e:
            print(f"[ERROR] Timeout during search: {e}")
        except WebDriverException as e:
            print(f"[ERROR] WebDriverException occurred: {e}")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}")

        self.save_debugging_artifacts()
        return False

    def check_no_results(self):
        """
        Check for a 'no results' message.
        """
        try:
            no_results_indicator = self.driver.find_element(By.XPATH, "//div[contains(text(), 'keine Ergebnisse')]")
            if no_results_indicator:
                print("[DEBUG] 'No Results' indicator found.")
                return True
        except Exception:
            pass
        return False

    def extract_results_with_pagination(self):
        """
        Paginate results, collecting company name + link.
        """
        base_url = "https://www.wlw.de"  # Convert relative links
        while True:
            try:
                company_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "span.line-clamp-2.md\\:line-clamp-1.break-anywhere"
                )
                if not company_elements:
                    print("[DEBUG] No company names found on this page.")
                else:
                    for company_span in company_elements:
                        name = company_span.text.strip()
                        link = ""
                        try:
                            parent_anchor = company_span.find_element(By.XPATH, "..")
                            relative_link = parent_anchor.get_attribute("href")
                            link = relative_link if relative_link.startswith("http") else base_url + relative_link
                        except Exception as ex:
                            print(f"[ERROR] Failed to extract link for {name}: {ex}")
                            link = ""
                        self.results.append({
                            "Company Name": name,
                            "Link": link
                        })
                        print(f"[INFO] Found company: {name} | Link: {link}")

                # Dismiss cookie popup if present
                if self.dismiss_cookie_popup():
                    print("[DEBUG] Cookie popup dismissed during pagination.")

                # Next page
                next_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.button.next[rel='next']"))
                )
                print("[DEBUG] 'Next' button found. Navigating to the next page...")
                next_button.click()
                time.sleep(2)

            except TimeoutException:
                print("[DEBUG] No 'Next' button found. Reached the last page.")
                break
            except NoSuchElementException:
                print("[DEBUG] No 'Next' button available. Pagination completed.")
                break
            except WebDriverException as e:
                print(f"[ERROR] WebDriverException during pagination: {e}")
                break

    def scrape_company_details_in_parallel(self, max_workers=5):
        """
        Parallel detail scraping. Each company detail is loaded with a separate headless driver.
        """
        def scrape_single_detail(company_dict):
            link = company_dict.get("Link", "")
            if not link:
                return company_dict

            # Setup a short-lifetime headless driver for concurrency
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            # disable images for speed
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)

            service = Service(ChromeDriverManager().install())
            local_driver = webdriver.Chrome(service=service, options=chrome_options)

            try:
                local_driver.get(link)
                time.sleep(1)  # short sleep

                # --- 1) Website (by clicking 'Mehr' or 'Website besuchen') ---
                website_url = "N/A"
                try:
                    website_button = WebDriverWait(local_driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn--subtle.btn--md.website-button"))
                    )
                    website_button.click()
                    # Wait for <a.website-button> after click
                    website_anchor = WebDriverWait(local_driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn--subtle.btn--md.website-button"))
                    )
                    website_url = website_anchor.get_attribute("href")
                except TimeoutException:
                    pass

                # --- 2) Phone number (click 'Telefonnummer') ---
                phone = "N/A"
                try:
                    phone_btn = WebDriverWait(local_driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.phone-button"))
                    )
                    phone_btn.click()
                    phone_elem = WebDriverWait(local_driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#tooltips a.copy-button span"))
                    )
                    phone = phone_elem.text.strip()
                except TimeoutException:
                    pass

                # --- 3) Address (using new selector)
                # Example snippet:
                # <div class="address flex items-center gap-2 font-copy-500">
                #   <span>Plauener Str. 163-165, DE-13053 Berlin</span>
                # </div>
                address = "N/A"
                try:
                    address_elem = WebDriverWait(local_driver, 2).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div.address.flex.items-center.gap-2.font-copy-500 span")
                        )
                    )
                    address = address_elem.text.strip()
                except TimeoutException:
                    pass

                # Update dict
                company_dict["Official Website"] = website_url
                company_dict["Phone"] = phone
                company_dict["Address"] = address
                return company_dict

            finally:
                local_driver.quit()

        # Use ThreadPoolExecutor for parallel scraping
        updated_entries = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_entry = {
                executor.submit(scrape_single_detail, entry): entry
                for entry in self.results
            }
            for future in as_completed(future_to_entry):
                original_entry = future_to_entry[future]
                try:
                    updated_entry = future.result()
                    updated_entries.append(updated_entry)
                except Exception as exc:
                    print(f"[ERROR] Exception in parallel detail scraping: {exc}")
                    updated_entries.append(original_entry)

        self.results = updated_entries

    def dismiss_cookie_popup(self):
        try:
            consent_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            )
            consent_button.click()
            print("[DEBUG] Cookie consent popup dismissed.")
            return True
        except TimeoutException:
            return False

    def save_debugging_artifacts(self):
        try:
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("[DEBUG] Current page source saved to debug_page_source.html.")
            self.driver.save_screenshot("search_results_error.png")
            print("[DEBUG] Screenshot saved: search_results_error.png")
        except Exception as e:
            print(f"[ERROR] Failed to save debugging artifacts: {e}")
