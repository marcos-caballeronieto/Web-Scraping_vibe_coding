import logging
import time
import random
import numpy as np
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# --- Configurations & Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_human_curve(start_pos, end_pos, num_points=20):
    """
    Generates a Bezier curve path simulating a human mouse movement.
    """
    p0 = start_pos
    p3 = end_pos
    
    # Introduce random control points for the curve
    p1 = (start_pos[0] + random.randint(-50, 50), start_pos[1] + random.randint(-50, 50))
    p2 = (end_pos[0] + random.randint(-50, 50), end_pos[1] + random.randint(-50, 50))
    
    points = []
    for t in np.linspace(0, 1, num_points):
        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]
        points.append((int(x), int(y)))
    return points

def perform_human_mouse_movements(driver):
    """
    Simulates erratic, curved human mouse movements on the page
    to help bypass Cloudflare Turnstile's behavioral analysis.
    """
    window_size = driver.get_window_size()
    max_x, max_y = window_size['width'], window_size['height']
    
    action = ActionChains(driver)
    
    # Fake a few random mouse movements
    current_pos = (random.randint(0, max_x//2), random.randint(0, max_y//2))
    
    for _ in range(3):
        target_pos = (random.randint(0, max_x-50), random.randint(0, max_y-50))
        curve = generate_human_curve(current_pos, target_pos)
        
        # We use move_by_offset to step through the curve
        for point in curve:
            x_offset = point[0] - current_pos[0]
            y_offset = point[1] - current_pos[1]
            try:
                action.move_by_offset(x_offset, y_offset).perform()
                current_pos = point
                time.sleep(random.uniform(0.01, 0.05)) # Fast, human-like micro pauses
            except Exception:
                # If offset is out of bounds, break iteration
                break
                
        # Longer pause at the end of a big movement
        time.sleep(random.uniform(0.3, 1.2))


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
        
        # Wait a bit, then mimic human interactions to pass CF
        time.sleep(3)
        logging.info("Performing human-like mouse generated curves...")
        perform_human_mouse_movements(driver)
        
        # Wait remainder of the time
        time.sleep(5)
        
        # Explicit wait for the job list to appear in DOM
        try:
            # The CSS layout has changed, 'jobsearch-ResultsList' may no longer be reliable.
            # We wait for the main list container which might be a <ul> or <div> that holds job items.
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#mosaic-provider-jobcards"))
            )
            logging.info("Job results loaded successfully.")
        except:
            logging.error("Timeout waiting for #mosaic-provider-jobcards. We might still be blocked.")
            # Save a screenshot to understand what Indeed is showing us
            driver.save_screenshot("indeed_timeout_debug.png")
            logging.info("Saved a screenshot to 'indeed_timeout_debug.png' for debugging.")
            return extracted_records
            
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_cards = soup.select('.job_seen_beacon') # Each individual job result card uses this class
        logging.info(f"Detected {len(job_cards)} list items on page.")
        
        for card in job_cards:
            # Title
            title_elem = card.select_one('h2.jobTitle span[title]') or card.select_one('h2.jobTitle')
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
        # Reset ActionChains mouse position (internal selenium quirk handling) Before quitting
        try:
            ActionChains(driver).move_to_element_with_offset(driver.find_element(By.TAG_NAME, 'body'), 0, 0).perform()
        except:
            pass
            
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
