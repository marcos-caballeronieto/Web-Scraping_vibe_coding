# Workflow: Web Scraping with AI Agent + Playwright MCP

## 🧠 The Concept
Instead of writing Playwright scripts line-by-line, we use an AI Assistant hooked up to a Playwright MCP (Model Context Protocol) server. 
* **The Agent** acts as the brain.
* **The MCP Server** acts as the bridge.
* **Playwright** acts as the hands and eyes.

You tell the AI *what* you want; the AI uses the MCP tools to drive the browser, inspect the DOM, and extract the data dynamically.

---

## ⚙️ Step 1: The Setup
1. **Initialize the Agent:** Open your AI coding environment (Cursor, Claude Code, etc.).
2. **Start the MCP Server:** Ensure the Playwright MCP server is running and connected to your AI. 
   *(The AI should now have access to tools like `playwright_navigate`, `playwright_evaluate`, `playwright_click`, etc.)*
3. **Target Acquired:** Have your target URL ready.

---

## 🗣️ Step 2: The Initial Prompting (The "Go Fetch")
Instead of writing code, you write instructions. 

**Example Prompt to the AI:**
> "Use your Playwright MCP to navigate to `http://quotes.toscrape.com/js/`. Inspect the page structure. I need to extract all the quotes, their authors, and the tags. Tell me what CSS selectors you find."

---

## 🔄 Step 3: The AI Execution Loop
Once prompted, the AI will enter an autonomous loop:

1. **Navigate:** The AI calls the MCP tool to open the URL in a headless browser.
2. **Inspect:** The AI uses the MCP to run `document.querySelectorAll()` or similar commands to view the raw HTML/DOM structure.
3. **Strategize:** The AI reads the DOM and determines the best Playwright Locators (e.g., `page.locator('.quote')`).
4. **Test & Refine:** If the site is dynamic, the AI might realize it needs to wait or scroll. It will adjust its MCP commands automatically until it successfully grabs the data.

---

## 💾 Step 4: Data Extraction and Output
Once the AI has successfully navigated the page and identified the right locators, ask it to finalize the output.

**Example Prompt:**
> "Great, those selectors look right. Now, use the MCP to extract all the data on page 1, format it as a JSON array, and save it to a file called `quotes_data.json`."

---

## 🧹 Step 5: Data Processing
After extracting raw data, it often needs to be cleaned and formatted before it is truly useful.

**Example Prompt:**
> "Now that we have the raw data, use a data analysis library like `pandas` to create a DataFrame. Clean the text by removing any leading or trailing whitespaces, convert numeric strings to floats, handle missing values, and export the final cleaned dataset to a file like `cleaned_data.csv`."

**What the AI does:**
1. **Load Data:** The AI reads the raw scraped data (e.g., from `quotes_data.json`).
2. **Clean Data:** It performs operations like text normalization, formatting, type conversion, and handling null/missing values.
3. **Export Data:** The structured, cleaned data is saved into a final destination format such as CSV, Parquet, or directly into a database.

---

## 🚨 Best Practices for this Workflow
* **Be Iterative:** Don't ask the AI to "scrape 50 pages and save to a database" in one go. Ask it to navigate first, inspect second, extract one item third, and *then* scale up.
* **Ask for the Script Later:** The MCP is great for live exploration. Once the AI successfully extracts the data via MCP, you can say: *"Now that we know the exact selectors and waiting strategy, write a standalone Python Playwright script that does this, so I can run it outside of this chat."*
* **Watch for Bot Protection:** If the MCP hangs or the AI reports a "Cloudflare" or "Access Denied" page, you will need to instruct the AI to change the user agent or add stealth headers.