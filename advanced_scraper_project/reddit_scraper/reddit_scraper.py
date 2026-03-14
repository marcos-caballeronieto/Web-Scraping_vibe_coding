import logging
import time
import requests
import pandas as pd

# --- Configurations & Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_reddit_json(subreddit_url, num_pages=3):
    """
    Scrapes Reddit using their native .json endpoint.
    This avoids headless browser blocks and parsing complex unpredictable UI.
    """
    extracted_records = []
    seen_titles = set()
    
    # We must provide a User-Agent to prevent Reddit from returning a 429 Too Many Requests
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    # Ensure URL ends with .json
    if not subreddit_url.endswith('.json') and not '?' in subreddit_url:
        base_url = subreddit_url.rstrip('/') + '.json'
    else:
        base_url = subreddit_url
        
    current_url = base_url
    
    for page_num in range(1, num_pages + 1):
        logging.info(f"Scraping Page {page_num} -> {current_url}")
        
        try:
            response = requests.get(current_url, headers=headers, timeout=15)
            if response.status_code != 200:
                logging.error(f"Failed to fetch data: HTTP {response.status_code}")
                # Sometimes reddit just rate limits for a minute
                break
                
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            if not posts:
                logging.info("No posts found. Ending pagination.")
                break
                
            for post in posts:
                # Post properties are cleanly exposed in the JSON
                post_data = post.get('data', {})
                raw_title = post_data.get('title', '').strip()
                raw_upvotes = str(post_data.get('score', 0))
                raw_comments = str(post_data.get('num_comments', 0))
                
                # Deduplicate and skip empty titles
                if not raw_title or raw_title in seen_titles:
                    continue
                    
                seen_titles.add(raw_title)
                extracted_records.append({
                    "post_title": raw_title,
                    "upvotes": raw_upvotes,
                    "comments": raw_comments
                })
                
            # Random emulation delay between pages is still polite
            time.sleep(2)
            
            # Pagination on Reddit JSON uses 'after' tokens
            after = data.get('data', {}).get('after')
            if not after:
                logging.info("No 'after' token found. Ending pagination.")
                break
                
            current_url = f"{base_url}?after={after}"
            
        except requests.exceptions.Timeout:
             logging.error("Request timed out.")
             break
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            break
            
    return extracted_records


def export_to_csv(records, filename="reddit_hardware_data.csv"):
    """Dumps the extracted JSON records into a CSV."""
    if not records:
        logging.warning("No records to export.")
        return
        
    df = pd.DataFrame(records)
    
    # Standardize column order
    columns = ["post_title", "upvotes", "comments"]
    df = df[columns]
    
    df.to_csv(filename, index=False, encoding='utf-8')
    logging.info(f"Successfully exported {len(df)} records to {filename}")


def main():
    target_url = "https://www.reddit.com/r/hardware/"
    logging.info("Starting Reddit JSON extraction...")
    
    records = scrape_reddit_json(target_url, num_pages=3)
    export_to_csv(records)
    logging.info("Extraction complete!")


if __name__ == "__main__":
    main()
