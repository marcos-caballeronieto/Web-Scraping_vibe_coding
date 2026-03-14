import json
import time
from playwright.sync_api import sync_playwright

def scrape_category(page, url):
    """
    Scrapes a single category page, clicks 'More' if present,
    and extracts all product information.
    """
    print(f"Navigating to {url}")
    try:
        page.goto(url, wait_until="networkidle")
    except Exception as e:
        print(f"Failed to navigate to {url}: {e}")
        return [], []

    # Extract any subcategory links from the sidebar to visit later
    new_categories = []
    try:
        links = page.locator("#side-menu a").all()
        for link in links:
            href = link.get_attribute("href")
            if href and "/test-sites/e-commerce/more" in href:
                full_url = "https://webscraper.io" + href if href.startswith("/") else href
                new_categories.append(full_url)
    except Exception as e:
        print(f"Error extracting subcategory links: {e}")

    # Click "More" button until it disappears
    # Wait a bit in case it's rendering
    time.sleep(1)
    while True:
        try:
            # Look for a button or link containing the text "More"
            # It's case-sensitive depending on the text on page. We also check "Load more" just in case
            load_more_buttons = page.locator("a.ecomerce-items-scroll-more")
            # Wait a brief moment to see if it's there
            if load_more_buttons.count() > 0 and load_more_buttons.first.is_visible():
                print("Clicking 'More' button...")
                load_more_buttons.first.click()
                time.sleep(1.5)  # give it time to load more elements
            else:
                break
        except Exception as e:
            # Note: Playwright throws if the element becomes detached while checking
            print(f"Stopping 'More' clicks on {url} due to: {e}")
            break

    products = []
    try:
        items = page.locator(".thumbnail").all()
        for item in items:
            product_info = {}
            try:
                product_info['title'] = item.locator(".title").inner_text(timeout=500)
            except:
                product_info['title'] = None
                
            try:
                product_info['price'] = item.locator(".price").inner_text(timeout=500)
            except:
                product_info['price'] = None
                
            try:
                product_info['description'] = item.locator(".description").inner_text(timeout=500)
            except:
                product_info['description'] = None
                
            try:
                product_info['reviews'] = item.locator(".ratings p.pull-right").inner_text(timeout=500)
            except:
                product_info['reviews'] = None

            products.append(product_info)
    except Exception as e:
        print(f"Error extracting items from {url}: {e}")

    return products, new_categories

def main():
    base_url = "https://webscraper.io/test-sites/e-commerce/more"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        categories_to_visit = [base_url]
        visited_categories = set()
        
        all_extracted_data = []
        
        while categories_to_visit:
            current_url = categories_to_visit.pop(0)
            if current_url in visited_categories:
                continue
                
            visited_categories.add(current_url)
            
            category_data, new_urls = scrape_category(page, current_url)
            
            # Add newly discovered URLs to the queue
            for url in new_urls:
                if url not in visited_categories and url not in categories_to_visit:
                    categories_to_visit.append(url)
            
            print(f"Extracted {len(category_data)} items from {current_url}")
            
            for item in category_data:
                item['category_url'] = current_url
            
            all_extracted_data.extend(category_data)
            
        print(f"\nTotal items extracted: {len(all_extracted_data)}")
        
        output_file = "scraped_products.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_extracted_data, f, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {output_file}")
        except Exception as e:
            print(f"Failed to save data: {e}")

        browser.close()

if __name__ == "__main__":
    main()
