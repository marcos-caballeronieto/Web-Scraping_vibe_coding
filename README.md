# Web Scraping Learning Project 🕸️

Welcome to my personal hands-on learning lab for Web Scraping and Data Extraction! 🚀 

This repository documents my journey from learning the absolute basics of static HTML parsing, all the way to building advanced, stealthy asynchronous scrapers capable of handling dynamic rendering, heavy anti-bot protections, and LLM-powered data structuring.

## 📖 Project Overview

The objective of this project was to progressively build up my web scraping skills. By tackling real-world targets with increasing levels of difficulty (e.g., Craigslist, Reddit, and Indeed), I gained practical experience with various tools, frameworks, and data processing techniques.

This project is structured into three main phases:

### Phase 1: The Fundamentals (Root Directory)
I started by writing standalone scripts and notebooks to understand the foundational concepts:
*   `1-Basic_Scraping.py`: Introduction to HTTP requests and static HTML parsing using `BeautifulSoup`.
*   `2-Dynamic_Sites_Scraping_Selenium.py`: Moving to dynamic DOMs with `Selenium` to handle JavaScript-heavy sites.
*   `3-Dynamic_Scraping_Playwright.py`: Upgrading from Selenium to `Playwright` for faster, modern, asynchronous browser automation.
*   `4-Playwrigth_MCP_workflow.md`: Notes on using Playwright in complex automated agent workflows.
*   `5-Data_Proccesing.ipynb`: A Jupyter Notebook dedicated to data cleaning, type coercion, and transitioning untidy scraped data into structured Pandas DataFrames.
*   `6-Other_Info+Interview.md`: Miscellaneous notes and interview prep related to web scraping.

### Phase 2: Building a Playwright Scraper (`/playwright_project`)
The next step was to consolidate the basics into a cohesive mini-project. 
*   **`web_scraper_project.py`**: A robust Playwright scraper designed to extract e-commerce product data.
*   **`data_cleaner.py`**: A separate utility to rigorously clean the extracted `.json` into a production-ready `.csv` file.

### Phase 3: The Advanced Scraper Toolkit (`/advanced_scraper_project`)
This is the core of the repository. Here, I built `advanced_scraper.py`, a highly flexible, stealth-oriented framework. This section explores modern hurdles like CAPTCHAs, bot-detection WAFs (Cloudflare/DataDome), and AI-driven element parsing.

#### Advanced Features Implemented:
*   **Anti-Bot Evasion**: Utilization of `playwright-stealth` and `undetected-chromedriver` to mask automation signatures.
*   **Proxy Rotation**: Integration of rotating datacenter/residential proxies via `.env` configuration.
*   **Human Emulation**: Built-in randomized delays and asynchronous human-like scrolling.
*   **LLM Parsing Integration**: Bypassing brittle CSS selectors by passing raw DOM snippets into an LLM, returning structured JSON perfectly typed via `Pydantic`.

#### Real-World Case Studies:
To test the advanced toolkit, I built three distinct adaptations targeting highly specific architectures:

1.  **Craigslist JSON-LD (`/craig_list_example`)**
    *   *Challenge:* Extracting granular specs and condition data efficiently from a list view.
    *   *Solution:* Bypassed traditional DOM parsing entirely by locating and extracting the embedded `application/ld+json` script tags directly.

2.  **Reddit Custom API Interception (`/reddit_scraper`)**
    *   *Challenge:* Reddit aggressively blocks headless browsers with login walls and serves extremely complex modern web components.
    *   *Solution:* Discovered and utilized Reddit's native JSON endpoint implementation (`.json` appended to the URL) to easily extract tens of thousands of `post_title`, `upvotes`, and `comments` using simple Python `requests`, completely bypassing front-end WAFs.

3.  **Indeed Anti-Bot Analysis (`/indeed_scraper`)**
    * *Challenge:* Indeed employs a multi-layered security approach, primarily using Cloudflare Turnstile and DataDome to heavily penalize bot IP reputations and monitor for automated behavior.
    * *Solution/Result:* Initial attempts using open-source stealth drivers (`playwright-stealth` and `undetected-chromedriver`) were successfully blocked by the WAF. To overcome this:
        * **Behavioral Evasion:** Specifically in order to not be blocked by Turnstile's behavioral analysis, I implemented mathematically generated **Bezier curves** (`numpy` and `scipy`) via `ActionChains` to simulate erratic, human-like mouse movements. 
        * **IP Reputation:** I utilized **mobile proxy tethering** (4G/5G) to leverage high-reputation CGNAT IP addresses, bypassing the strict IP bans.
        * **Dynamic DOM Parsing:** Once past the security wall, I utilized my **Playwright MCP** workflow to inspect the rendered page and discover Indeed's newly updated CSS containers (identifying `#mosaic-provider-jobcards` instead of the legacy lists). 
    * **Final Outcome:** This combined approach successfully bypassed the protections and reliably extracted the target job data into a structured CSV.

## 🛠️ Technology Stack
* **Languages:** Python 3.11
* **Web Automation:** `playwright`, `playwright-stealth`, `selenium`, `undetected-chromedriver`, Playwright MCP
* **Behavioral Emulation:** `numpy`, `scipy` (used to generate Bezier curves for human-like mouse movements)
* **Parsing:** `beautifulsoup4`, `json`, `pydantic`
* **Data Processing:** `pandas`, `jupyter`
* **Network:** `requests`, Standard proxy implementation, Mobile proxy tethering (4G/5G for high-reputation CGNAT IPs)

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/marcos-caballero/Web-Scraping_vibe_coding.git
    cd Web-Scraping_vibe_coding
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r advanced_scraper_project/requirements.txt
    playwright install chromium
    ```

3.  **Environment Variables:**
    To use the advanced anti-bot features, copy `.env.example` to `.env` inside `advanced_scraper_project` and add your rotating proxy URI.

## 📝 Key Takeaways
This project taught me that web scraping is rarely just about writing CSS selectors. The true challenge lies in adapting to the target's architecture—whether that means leveraging embedded JSON-LD, intercepting hidden APIs, or fighting advanced edge-protection WAFs. 

Happy Scraping! 🕷️
