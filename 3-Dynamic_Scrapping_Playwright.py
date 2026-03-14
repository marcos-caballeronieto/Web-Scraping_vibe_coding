# ==========================================
# Phase 1: Imports - Bringing in our Tools
# ==========================================

# We import sync_playwright from the playwright library.
# Playwright supports both synchronous (blocks until finished) and 
# asynchronous (can run multiple things at once) code. For beginners,
# synchronous is much easier to read and reason about.
from playwright.sync_api import sync_playwright

def scrape_playwright_quotes():
    url = "http://quotes.toscrape.com/js/"

    # ==========================================
    # Phase 2: The Context Manager
    # ==========================================
    
    # WHY USE THE `with sync_playwright() as p:` BLOCK?
    # Playwright communicates with actual browser processes behind the scenes
    # using WebSockets and underlying Node.js tools. 
    # Setting up and tearing down this entire engine safely is complex.
    # The `with ... as p:` block is Python's "Context Manager". It guarantees that
    # the moment your code finishes (or even if it crashes with an error), Python 
    # will automatically and cleanly shut down the Playwright engine. You don't 
    # need to remember to write a complex `try...finally: p.stop()` block.
    with sync_playwright() as p:
        
        # ==========================================
        # Phase 3: Browser vs. Context vs. Page
        # ==========================================
        
        # 1. THE BROWSER
        # First, we launch the physical browser executable (like Chromium/Chrome).
        # headless=True is the default (invisible), but we set it to True explicitly here.
        # headless=False would pop open a visible window so you can watch it.
        print("Launching the Chromium browser...")
        browser = p.chromium.launch(headless=True)
        
        # 2. THE BROWSER CONTEXT
        # WHY IS THIS IMPORTANT?
        # A "Context" is like opening a completely fresh "Incognito Window". 
        # It has its own cookies, its own cache, and its own local storage. 
        # If you wanted to test logging in as 5 different users simultaneously,
        # you would create 1 Browser, but 5 different Contexts. This is incredibly 
        # lightweight and fast compared to launching 5 completely separate Browsers 
        # (which is what you'd often have to do in older Selenium versions).
        context = browser.new_context()

        # 3. THE PAGE
        # A Page is simply a single tab inside that Context.
        page = context.new_page()

        # ==========================================
        # Phase 4: Navigation and Auto-waiting
        # ==========================================
        
        print(f"Navigating to {url} ...")
        # Go to the URL. Note that Playwright automatically waits until the initial
        # network load is finished to proceed.
        page.goto(url)

        # WHY DON'T WE NEED EXPLICIT WAITS LIKE IN SELENIUM?
        # In Selenium, we had to write: `wait.until(EC.presence_of_element_located(...))`
        # because Selenium tries to grab the element instantly and crashes if it's missing.
        # Playwright has "Auto-waiting" built into its DNA. 
        # Whenever you ask Playwright to click a button or read text, it will automatically:
        #   1. Wait for the element to exist in the DOM.
        #   2. Wait for it to become visible (not hidden by CSS).
        #   3. Wait for it to stop animating/moving.
        # If it doesn't happen within the default timeout (usually 30 seconds), it throws an error.
        # This eliminates 90% of the flaky behavior and boilerplate code found in Selenium scripts.
        print("Waiting for quotes to appear and grabbing them...")

        # ==========================================
        # Phase 5: Locators
        # ==========================================
        
        # WHAT IS A LOCATOR AND WHY IS IT RECOMMENDED?
        # In Selenium, `driver.find_element()` immediately searches the page right that second.
        # If you save it to a variable, and the page updates 2 seconds later, that variable
        # becomes "stale" and crashes your script if you try to use it.
        # 
        # A Playwright `Locator` is fundamentally different. It is an *instruction* on how 
        # to find an element, not the element itself. 
        # `page.locator(".quote")` means: "Whenever I ask you to do something with this variable, 
        # go look for elements with the class '.quote' at that exact moment."
        # This makes Locators incredibly resilient to dynamically changing web pages.
        
        # We create a locator for all quote blocks.
        quotes_locator = page.locator(".quote")
        
        # Wait for the elements to actually be there (Playwright does this securely) 
        # and count them.
        count = quotes_locator.count()
        print(f"Successfully found {count} quotes!\n")

        # Loop through the count. (Playwright's nth(i) is 0-indexed)
        for i in range(count):
            # We get a specific quote block (e.g., the 0th quote, the 1st quote)
            quote_block = quotes_locator.nth(i)
            
            # Now we create locators INSIDE that specific block.
            # `inner_text()` triggers Playwright's auto-wait: it waits for the element
            # to be visible, then grabs the text. No explicit sleeps needed!
            text = quote_block.locator(".text").inner_text()
            author = quote_block.locator(".author").inner_text()
            
            print(f"Quote: {text}")
            print(f"Author: {author}")
            print("-" * 40)

        # We close the browser to free up resources.
        # Note: If we forgot this, the Context Manager `with` block above 
        # would actually still clean up the underlying engine for us, but it's
        # good practice to close the browser explicitly.
        print("\nClosing the browser...")
        browser.close()

if __name__ == "__main__":
    scrape_playwright_quotes()

# ==========================================
# Why Modern Developers Often Prefer Playwright over Selenium
# ==========================================
# 
# 1. Built-in Auto-Waiting: The biggest headache in dynamic web scraping is "flakiness" 
#    (scripts that randomly crash because a page loaded 0.5s too slow). Selenium requires 
#    verbose, manual "Explicit Waits" for almost every action. Playwright automatically waits 
#    for elements to be ready (visible, stable, enabled) before interacting with them, 
#    drastically reducing code size and crashes.
# 
# 2. Resilient Locators: Selenium's elements go "stale" if the webpage Javascript updates 
#    the screen after you've found them. Playwright's Locators act as active search queries 
#    that re-evaluate at the exact moment you perform an action, completely eliminating 
#    StaleElementReferenceExceptions.
# 
# 3. Contexts over Browsers: Playwright introduced "Browser Contexts", allowing you to spin 
#    up isolated, lightweight "incognito" sessions in milliseconds using the same browser 
#    instance. Selenium often required launching entirely new, heavy browser windows for 
#    isolated sessions, eating up RAM.
# 
# 4. Built for the Modern Web: Playwright was built by Microsoft specifically to understand 
#    modern frameworks (React, Vue, SPA) and can easily intercept network requests, mock APIs, 
#    and even tap into WebSockets out-of-the-box, things that were notoriously difficult 
#    to configure in older versions of Selenium.
