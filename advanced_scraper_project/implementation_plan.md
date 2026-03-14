# Role
You are a Lead Data Engineering Architect specializing in resilient web scraping, anti-bot evasion, and AI Agent workflows.

# Objective
Write a robust, production-ready Python script using Playwright. The script must bypass standard anti-bot protections using stealth and proxy rotation, navigate dynamic content (Infinite Scroll and "Load More" buttons), extract raw HTML, and use an LLM with Pydantic to parse that unstructured data into a strict schema.

# Tech Stack
- Python 3.11+
- `playwright` (Sync API)
- `playwright-stealth`
- `pydantic` (v2)
- `openai` (or equivalent LLM SDK, utilizing Structured Outputs)
- `pandas`
- `python-dotenv`

# System Architecture & Requirements

## 1. Anti-Bot Infrastructure & Stealth (Priority 1)
- **Stealth Injection:** Import `playwright-stealth` and apply `stealth_sync` to the browser context to mask automation signatures (e.g., hiding `navigator.webdriver`, spoofing user agents and webgl vendors).
- **Proxy Management:** Read a `PROXY_LIST` (comma-separated string) from a `.env` file. Implement a function to select a random proxy for the browser context. Include a try/except fallback so if the proxy times out, the script retries with a new proxy or falls back to the local connection for testing.
- **Human Emulation:** Do not use hardcoded `time.sleep()`. Instead, implement a helper function that generates a randomized delay (e.g., `random.uniform(1.2, 3.5)`) to use between major interactions (like scrolling or clicking) to mimic human pacing.

## 2. Dynamic Navigation (Infinite Scroll & Pagination)
- Initialize the browser in headless mode and navigate to the target URL.
- **Infinite Scroll Handler:** Write a dedicated function that executes JavaScript (`window.scrollTo(0, document.body.scrollHeight)`) to scroll down. 
- **Scroll Validation:** After scrolling, wait for the network to idle (`page.wait_for_load_state('networkidle')`). Compare the `document.body.scrollHeight` before and after. Break the loop only when the height stops changing after 2 consecutive attempts.
- **"Load More" Fallback:** After scrolling finishes, check if an element matching `#load-more-btn` (or similar) exists. If it does, click it, wait for network idle, and resume the scroll check.

## 3. Unstructured Data Extraction
- Do not rely on brittle, granular CSS selectors for individual data points (like prices or titles).
- Target the main outer container (e.g., the grid or list wrapper) and extract its `inner_text` or stripped raw HTML.
- **CAPTCHA Check:** Before extracting data, check the page title or body text for common CAPTCHA flags (e.g., "Access Denied", "Cloudflare", "Verify you are human"). If detected, log a critical error and initiate a retry with a different proxy.

## 4. LLM Parsing & Schema Definition (Pydantic)
- Define a strict Pydantic model called `ItemListing` containing: `title` (str), `price` (float, nullable), `stock_status` (str), and `features` (list[str]).
- Define a wrapper model `ExtractedData` containing `list[ItemListing]`.
- Pass the massive raw text string extracted in Step 3 to the LLM API using the Native Structured Outputs feature.
- Prompt the LLM to: "Act as a data parser. Extract every product from this raw text. Clean the data (remove currency symbols, cast prices to float, determine stock status) and map it perfectly to the provided schema."

## 5. Processing & Export
- Take the validated Pydantic object returned by the LLM.
- Convert it into a list of dictionaries using `.model_dump()`.
- Load the dictionaries into a Pandas DataFrame.
- Export to `resilient_scraper_output.csv` without the index.

## 6. Code Structure & Logging
- Ensure the code is highly modular. Use discrete functions like `setup_browser()`, `handle_pagination()`, `extract_raw_data()`, and `parse_with_llm()`.
- Use the `logging` module (INFO level) to print updates to the console (e.g., "Proxy assigned...", "Scrolling page...", "LLM parsing complete...").
- Include a standard `if __name__ == "__main__":` block.