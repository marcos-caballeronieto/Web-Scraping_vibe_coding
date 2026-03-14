import os
import time
import random
import logging
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import Stealth
from pydantic import BaseModel
import pandas as pd
from openai import OpenAI

# ==========================================
# Application Configuration & Scaling Concepts
# ==========================================
# 1. We load environment variables using python-dotenv.
#    This allows us to keep sensitive keys (like OPENAI_API_KEY) and configurable
#    settings (like PROXY_LIST) out of the source code, maximizing reproducibility
#    and scaling across different environments (dev, staging, production).
load_dotenv()

# 2. We use the built-in logging module instead of simple print() statements.
#    In a production workflow, logs can be sent to services like Datadog or ELK.
#    The INFO level is sufficient for standard tracking.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==========================================
# Schema Definitions (Pydantic for LLM constraint)
# ==========================================
# By using Pydantic, we guarantee that any data extracted by the LLM strictly conforms
# to this shape. If the LLM hallucinates an invalid type, OpenAI's native structured 
# outputs feature will catch it or correct it before returning.

class ItemListing(BaseModel):
    title: str
    price: float | None
    stock_status: str
    features: list[str]

class ExtractedData(BaseModel):
    items: list[ItemListing]

# ==========================================
# Helper Functions (Anti-Bot & Human Emulation)
# ==========================================
def random_delay(min_sec=1.2, max_sec=3.5):
    """
    Emulates human pacing by sleeping for a random duration between actions.
    This avoids tripping basic rate limiters that look for exact intervals.
    Instead of hardcoding time.sleep(2), which is easily flagged by bots.
    """
    delay = random.uniform(min_sec, max_sec)
    logging.info(f"Sleeping for {delay:.2f} seconds to emulate human behavior...")
    time.sleep(delay)

def get_random_proxy():
    """
    Reads the PROXY_LIST from .env and returns a random proxy dictionary 
    formatted for Playwright context injection.
    Resilience: Returns None if no proxies are defined, falling back to local IP.
    """
    proxy_str = os.getenv("PROXY_LIST", "")
    if not proxy_str:
        return None
    proxies = [p.strip() for p in proxy_str.split(",") if p.strip()]
    if not proxies:
        return None
    
    selected_proxy = random.choice(proxies)
    logging.info(f"Selected proxy payload: {selected_proxy}")
    # Note: A real proxy might also need username/password configuration.
    return {"server": selected_proxy}

# ==========================================
# Core Scraper Logic
# ==========================================
def setup_browser(p):
    """
    Sets up the Playwright browser. 
    1. It implements playwright-stealth to mask navigator.webdriver signatures.
    2. It conditionally injects proxies.
    3. Runs headless by default for production CI/CD scaling.
    """
    proxy_config = get_random_proxy()
    
    # Launch browser. We keep headless=True for production speed and scaling.
    browser = p.chromium.launch(headless=True)
    
    # Create an isolated context. Contexts are faster than opening full new browsers.
    if proxy_config:
        context = browser.new_context(proxy=proxy_config)
    else:
        logging.info("No proxy supplied. Proceeding with local connection.")
        context = browser.new_context()
        
    page = context.new_page()
    
    # Stealth is now applied globally via the context manager in main()
    # stealth_sync(page) -> Removed
    
    return browser, page

def handle_pagination(page):
    """
    Handles dynamic content loading (Infinite Scroll and "Load More" buttons).
    This function scrolls dynamically, waits for network inactivity, and retries.
    """
    logging.info("Initiating infinite scroll handling...")
    same_height_count = 0
    max_same_height = 2  # End loop if scroll height doesn't change twice in a row
    
    last_height = page.evaluate("document.body.scrollHeight")
    
    while same_height_count < max_same_height:
        # Evaluate raw JavaScript to scroll directly to the bottom of the body element
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        random_delay() # Human scrolling delay
        
        try:
            # Wait until there are almost no active network requests (images loading, API calls)
            page.wait_for_load_state('networkidle', timeout=5000)
        except TimeoutError:
            # Silence timeout if a long-polling request prevents network idle
            pass
            
        new_height = page.evaluate("document.body.scrollHeight")
        
        if new_height == last_height:
            same_height_count += 1
            logging.info(f"Scroll height unchanged. Attempt {same_height_count}/{max_same_height}")
            
            # Fallback: Instead of just scroll, try to find a explicit matching button
            # We look for a few common Load More CSS signatures, including the specific one from the target site.
            try:
                load_more_btn = page.locator("a.ecomerce-items-scroll-more, #load-more-btn, button:has-text('Load more')").first
                if load_more_btn.is_visible():
                    logging.info("Detected 'Load More' button. Clicking...")
                    load_more_btn.click()
                    random_delay(2.0, 4.0)
                    same_height_count = 0  # Re-zero the counter because we successfully pushed a button
            except Exception as e:
                logging.debug(f"Attempted Load More interaction skipped: {e}")
        else:
            # Content loaded! Reset the same height counter.
            same_height_count = 0
            
        last_height = new_height
        
    logging.info("Finished pagination/scrolling routines.")

def extract_raw_data(page):
    """
    Inspects page content for specific CAPTCHA keywords.
    If clear, it grabs the macro-level text from the container, relying on the LLM 
    to sort out the structure later.
    """
    logging.info("Analyzing page for CAPTCHAs...")
    body_text = page.locator("body").inner_text().lower()
    title = page.title().lower()
    
    # Priority 3: Captcha detection system.
    captcha_keywords = ["access denied", "cloudflare", "verify you are human", "captcha"]
    if any(keyword in title for keyword in captcha_keywords) or any(keyword in body_text for keyword in captcha_keywords):
        logging.critical("CAPTCHA or Bot Protection barrier detected! Aborting extraction.")
        raise Exception("CAPTCHA detected. Consider rotating proxy or user agent.")
        
    logging.info("Page looks clean! Extracting raw macro-data...")
    
    # We avoid brittle DOM paths (.title, .description) because websites update CSS frequently.
    # Instead, we pull a massive unified text dump and handle complexity in the LLM.
    try:
        # First attempt: Try to isolate the specific grid wrap if possible (saves tokens)
        raw_content = page.locator(".col-lg-9").inner_text(timeout=5000)
    except TimeoutError:
        # Second attempt: Pull the entire body text
        raw_content = page.locator("body").inner_text()
        
    logging.info(f"Successfully extracted {len(raw_content)} raw characters.")
    return raw_content

def parse_with_llm(raw_text):
    """
    Passes unstructured text into OpenAI utilizing 'Structured Outputs' 
    (Supported in beta in newer OpenAI SDKs, or via Instructor).
    It guarantees type-safety and formatting without regex gymnastics.
    """
    logging.info("Transmitting raw data to LLM for parsing and mapping...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.warning("OPENAI_API_KEY not found in .env! Skipping parsing module.")
        # Return an empty schema array so the rest of the script doesn't crash
        return ExtractedData(items=[])
        
    client = OpenAI(api_key=api_key)
    
    prompt = (
        "Act as an expert data parsing agent. Extract every single product listing from this text. "
        "Clean the data comprehensively: remove currency symbols like $, cast prices to float, "
        "determine the item's stock status based on context, and map it perfectly to the provided JSON schema."
    )
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini", # Utilizing a fast/cheap model appropriate for data ETL
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text}
            ],
            response_format=ExtractedData,
        )
        
        parsed_data = completion.choices[0].message.parsed
        logging.info(f"LLM successfully parsed {len(parsed_data.items)} perfectly structured items.")
        return parsed_data
        
    except Exception as e:
        logging.error(f"LLM API Call failed: {e}")
        return ExtractedData(items=[])

# ==========================================
# Primary Invocation Wrapper
# ==========================================
def main():
    target_url = "https://webscraper.io/test-sites/e-commerce/more/computers/laptops"
    
    with Stealth().use_sync(sync_playwright()) as p:
        browser, page = setup_browser(p)
        
        try:
            logging.info(f"Executing navigation pipeline for -> {target_url}")
            page.goto(target_url, wait_until="domcontentloaded")
            random_delay(2.0, 3.5)
            
            # 1. Manage scrolling and expansion
            handle_pagination(page)
            
            # 2. Grab text payload
            raw_text = extract_raw_data(page)
            
            # 3. Clean and map with LLM
            extracted_schema = parse_with_llm(raw_text)
            
            # 4. Final Processing (DataFrame conversion & export)
            if extracted_schema.items:
                # Convert the Pydantic models back to standard Python dicts for Pandas
                items_dict = [item.model_dump() for item in extracted_schema.items]
                df = pd.DataFrame(items_dict)
                
                output_csv = "resilient_scraper_output.csv"
                df.to_csv(output_csv, index=False)
                logging.info(f"Pipeline Complete: {len(df)} records safely shipped to {output_csv}")
            else:
                logging.warning("No records were passed down from the LLM parser. Check token limits or input data.")
                
        except Exception as e:
            logging.error(f"A critical error occurred in the scraping workflow: {e}")
        finally:
            logging.info("Closing browser session and freeing memory...")
            browser.close()

if __name__ == "__main__":
    main()
