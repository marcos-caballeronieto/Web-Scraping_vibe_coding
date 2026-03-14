import logging
import json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import Stealth
import pandas as pd
import os

# --- Configurations & Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()


def setup_browser(p):
    proxy_envs = os.getenv("PROXY_LIST")
    proxy_config = None
    if proxy_envs:
        proxy_url = proxy_envs.split(',')[0]
        proxy_config = {"server": proxy_url}
        logging.info(f"Applying proxy configuration: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")
    else:
        logging.info("No proxy supplied. Proceeding with local connection.")

    browser = p.chromium.launch(
        headless=True,
        proxy=proxy_config,
        args=["--disable-blink-features=AutomationControlled"]
    )
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    return browser, page


def clean_price(price_str):
    if price_str is None:
        return 0.0
    try:
        price_str = str(price_str).replace('$', '').replace(',', '').strip()
        return float(price_str)
    except ValueError:
        return 0.0


def parse_cl_json_ld(page):
    logging.info("Searching for Craigslist JSON-LD structured data...")
    try:
        # CraigsList `application/ld+json` blocks
        locator = page.locator('#ld_searchpage_results')
        locator.wait_for(state='attached', timeout=10000)
        
        raw_json_text = locator.text_content()
        data = json.loads(raw_json_text)
        
        # Craigslist structures it as: {"@type": "ItemList", "itemListElement": [ {"@type":"ListItem", "position":"...", "item": {...} } ] }
        if not data or "@type" not in data or data["@type"] != "ItemList":
            logging.warning("JSON-LD structure is not an ItemList. Unable to parse.")
            return []
            
        elements = data.get("itemListElement", [])
        logging.info(f"Found {len(elements)} items in the JSON-LD structure.")
        
        extracted_records = []
        for element in elements:
            # Each element is a ListItem, and the core data is inside "item"
            item = element.get("item", {})
            if not item:
                # Sometimes Craigslist omits the nested "item" wrapper if structure varies
                if "name" in element:
                    item = element
                else:
                    continue
            
            # --- Extract ---
            raw_name = item.get("name", "")
            raw_desc = item.get("description", "")
            
            # Navigate nested 'offers' dict for price
            offers = item.get("offers", {})
            raw_price = offers.get("price", "0.0")
            
            # --- Clean ---
            clean_name = raw_name.strip()
            # If description is empty from JSON-LD, specs will just rely on parsing the title
            clean_specs = raw_desc.strip() 
            clean_price_val = clean_price(raw_price)
            
            # --- Condition Inference ---
            condition = "Unknown"
            lower_name = clean_name.lower()
            if any(k in lower_name for k in ["brand new", "sealed", "bnib", "new in box"]):
                condition = "New"
            elif "like new" in lower_name:
                condition = "Like New"
            elif "refurb" in lower_name:
                condition = "Refurbished"
            elif "used" in lower_name:
                condition = "Used"
            elif "parts" in lower_name or "repair" in lower_name or "broken" in lower_name:
                condition = "For Parts/Repair"
            elif "new" in lower_name:
                condition = "New"

            # --- Specs Inference ---
            import re
            extracted_specs = []
            
            # Look for storage (GB/TB)
            storage_match = re.findall(r'(\d+)\s*(?:gb|tb)(?:\s+ssd|\s+hdd|\s+hd|\s+storage)?', lower_name)
            if storage_match:
                extracted_specs.append(storage_match[-1] + "GB/TB Storage/RAM")
                
            # Look for CPU (i5, i7, i9, m1, m2, ryzen)
            cpu_match = re.findall(r'(i[3579]|m[123]|ryzen\s?\d|xeon)', lower_name)
            if cpu_match:
                extracted_specs.append("CPU: " + cpu_match[0].upper())
                
            # Look for Screen Size
            screen_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:"|-inch|inch)', lower_name)
            if screen_match:
                extracted_specs.append("Screen: " + screen_match[0] + '"')

            if extracted_specs:
                if clean_specs:
                    clean_specs += " | Extracted Specs: " + ", ".join(extracted_specs)
                else:
                    clean_specs = ", ".join(extracted_specs)
            else:
                if not clean_specs:
                    clean_specs = "Not specified"
                
            extracted_records.append({
                "item_name": clean_name,
                "price": clean_price_val,
                "condition": condition,
                "specs": clean_specs
            })
            
        return extracted_records

    except TimeoutError:
        logging.error("Timeout: JSON-LD script block not found on the page.")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON-LD block: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error during parsing: {e}")
        return []


def export_to_csv(records, filename="craigslist_sys_data.csv"):
    if not records:
        logging.warning("No records to export. Skipping CSV generation.")
        return
        
    df = pd.DataFrame(records)
    columns = ["item_name", "price", "condition", "specs"]
    df = df[columns]
    
    df.to_csv(filename, index=False, encoding='utf-8')
    logging.info(f"Successfully exported {len(df)} records to {filename}")


def main():
    target_url = "https://newyork.craigslist.org/search/sys"
    
    with Stealth().use_sync(sync_playwright()) as p:
        browser, page = setup_browser(p)
        try:
            logging.info(f"Navigating to -> {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
            
            # Optional: Add small delay to let React components hydrate and render the JSON-LD block
            page.wait_for_timeout(3000)
            
            records = parse_cl_json_ld(page)
            export_to_csv(records)
            
        except Exception as e:
            logging.error(f"Critical execution error: {e}")
        finally:
            logging.info("Closing browser session and freeing memory...")
            browser.close()

if __name__ == "__main__":
    main()
