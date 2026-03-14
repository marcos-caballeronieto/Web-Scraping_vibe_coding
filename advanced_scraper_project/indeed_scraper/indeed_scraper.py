import logging
import time
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# --- Configurations & Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scraper(target_url):
    """
    Runs undetected_chromedriver to bypass Indeed's Cloudflare check.
    Extracts the rendered HTML using BeautifulSoup.
    """
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-size=1920,1080")
    
    # Needs to be headful for Turnstile bypass
    logging.info("Starting undetected-chromedriver (Headful)...")
    driver = uc.Chrome(options=options, headless=False, version_main=145)
    
    extracted_records = []
    
    try:
        logging.info("Navigating to Indeed...")
        driver.get(target_url)
        
        # Wait a long time to allow the Cloudflare challenge to pass
        time.sleep(10)
        
        # Explicit wait for the job list to appear in DOM
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobsearch-ResultsList"))
            )
            logging.info("Job results loaded successfully.")
        except:
            logging.error("Timeout waiting for jobsearch-ResultsList. We might still be blocked.")
            return extracted_records
            
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_cards = soup.select('ul.jobsearch-ResultsList > li')
        logging.info(f"Detected {len(job_cards)} list items on page.")
        
        for card in job_cards:
            # Title
            title_elem = card.select_one('h2.jobTitle')
            if not title_elem:
                continue
                
            raw_title = title_elem.get_text(strip=True)
            
            # Company
            company_elem = card.select_one('[data-testid="company-name"]')
            raw_company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Location
            location_elem = card.select_one('[data-testid="text-location"]')
            raw_location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            extracted_records.append({
                "job_title": raw_title,
                "company": raw_company,
                "location": raw_location
            })
            
    except Exception as e:
        logging.error(f"Execution error: {e}")
    finally:
        driver.quit()
        
    return extracted_records

def export_to_csv(records, filename="indeed_jobs_data.csv"):
    if not records:
        logging.warning("No records to export. CSV not created.")
        return
        
    df = pd.DataFrame(records)
    columns = ["job_title", "company", "location"]
    df = df[columns]
    
    df.to_csv(filename, index=False, encoding='utf-8')
    logging.info(f"Successfully exported {len(df)} records to {filename}")


def main():
    target_url = "https://www.indeed.com/q-llm-optimization-jobs.html"
    logging.info("Initializing Indeed Scraper...")
    
    records = run_scraper(target_url)
    
    if records:
        export_to_csv(records)
    else:
        logging.error("Extraction failed.")

if __name__ == "__main__":
    main()
