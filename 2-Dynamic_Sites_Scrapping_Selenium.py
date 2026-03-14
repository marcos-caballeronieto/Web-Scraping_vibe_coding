# ==========================================
# Phase 1: Imports - Bringing in our Tools
# ==========================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def scrape_dynamic_quotes():
    # The URL of the site we want to scrape. Note the "/js/" at the end.
    # If you open this without JavaScript (like requests/BeautifulSoup does), it's blank!
    url = "http://quotes.toscrape.com/js/"

    # ==========================================
    # Phase 2: Initializing the WebDriver
    # ==========================================
    
    # WHY DO WE NEED A WEBDRIVER?
    # Unlike 'requests' which just downloads HTML raw text, Selenium is a browser automation tool.
    # It literally opens a real web browser (like Chrome, Firefox, or Edge), 
    # navigates to the page, and executes the JavaScript on that page just like a real user would. 
    # The 'WebDriver' is the software component that bridges our Python code to the actual browser.
    
    # WHAT IS "HEADLESS" MODE AND WHY USE IT?
    # By default, Selenium will pop open a visible browser window. This is great for debugging 
    # because you can see what the bot is doing. However, drawing a graphical window takes a lot of 
    # computer resources (CPU and Memory). 
    # "Headless" mode tells the browser to run in the background without a visible user interface.
    # Once your script works perfectly, you turn on headless mode to make your scraper run much 
    # faster and consume fewer resources, especially useful if running on a server.
    
    options = webdriver.ChromeOptions()
    # Uncomment the line below to run without opening a visible browser window:
    options.add_argument("--headless=new") 
    
    # We initialize the Chrome browser using our options.
    print("Launching the Chrome browser...")
    driver = webdriver.Chrome(options=options)

    # ==========================================
    # Phase 3: Try / Finally Block for Safety
    # ==========================================
    try:
        # Tell the browser to navigate to our URL.
        print(f"Navigating to {url} ...")
        driver.get(url)

        # ==========================================
        # Phase 4: Waiting Strategies (Crucial!)
        # ==========================================
        
        # WHY IS WAITING ESSENTIAL FOR DYNAMIC SITES?
        # When driver.get(url) finishes, the basic empty HTML structure might be loaded, 
        # but the JavaScript might still be downloading from the server to build the quotes.
        # If we try to extract the quotes immediately, Selenium will find 0 quotes and fail.
        
        # WHY IS time.sleep() A BAD IDEA?
        # A beginner might do `time.sleep(5)`. But if the internet is fast and it loads in 1 second,
        # you just wasted 4 seconds. If the internet is slow and it takes 6 seconds, your script 
        # still crashes. It's inflexible and unreliable.
        
        # EXPLICIT WAITS: The Professional Approach
        # We tell Selenium: "Wait for a maximum of 10 seconds. Keep constantly checking the page. 
        # The split second that a specific element appears on the screen, proceed immediately."
        # This is incredibly fast and resilient.
        
        print("Waiting for the quotes to be rendered by JavaScript...")
        # We create a "waiter" that will wait up to 10 seconds.
        wait = WebDriverWait(driver, 10)
        
        # We define our expected condition (EC). We want it to wait until at least one element
        # with the class 'quote' is "present" in the DOM (the structure of the page).
        # We use a tuple (By.CLASS_NAME, 'quote') to specify how to find the element.
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))

        # ==========================================
        # Phase 5: Locating Elements
        # ==========================================
        
        # HOW TO USE THE `By` CLASS:
        # Selenium gives you different strategies to point to elements on the page.
        # The `By` class provides these locators. We can find by ID, NAME, CLASS_NAME, 
        # XPATH, or CSS_SELECTOR. CSS_SELECTOR is often the easiest as it matches 
        # how you style things in CSS (e.g., '.quote' means class quote).
        
        # Find all blocks containing quotes.
        quote_elements = driver.find_elements(By.CSS_SELECTOR, ".quote")
        print(f"Successfully found {len(quote_elements)} quotes!\n")

        # Loop through each block to extract text and author.
        for element in quote_elements:
            # We search INSIDE the current element, not the whole driver.
            # Using By.CSS_SELECTOR '.text' finds the tag with class="text" inside this block.
            text = element.find_element(By.CSS_SELECTOR, ".text").text
            author = element.find_element(By.CSS_SELECTOR, ".author").text
            
            print(f"Quote: {text}")
            print(f"Author: {author}")
            print("-" * 40)

    except TimeoutException:
         print("Error: The page took too long to load or the elements didn't appear.")
    except WebDriverException as e:
         print(f"An error occurred with the browser: {e}")
         
    # ==========================================
    # Phase 6: Teardown
    # ==========================================
    finally:
        # WHY IS driver.quit() SO IMPORTANT?
        # When Selenium opens Chrome, a real Chrome process starts running on your computer.
        # If your script crashes or finishes and you don't call .quit(), that browser window
        # (or invisible background process if headless) stays open forever. 
        # If you run your script 50 times, you'll have 50 Chrome browsers silently eating all
        # your RAM and crashing your computer.
        # By putting `driver.quit()` inside a `finally:` block, we guarantee that Python will
        # close the browser, EVEN IF an error/crash happened in the `try:` block above.
        print("\nClosing the browser...")
        driver.quit()

if __name__ == "__main__":
    scrape_dynamic_quotes()

# ==========================================
# Comparing the Mindsets: requests/BS4 vs. Selenium
# ==========================================
# 
# 1. The requests + BeautifulSoup Mindset: The "Downloader"
#    - Mental Model: You are acting like a super-fast download manager. You send a letter 
#      (Request), receive a giant text file back (Response), and then use a magnifying 
#      glass (BS4) to search that text document for the data you want. 
#    - Speed & Stealth: It is incredibly fast and uses almost zero RAM. However, it cannot 
#      click buttons, it cannot scroll, and it cannot run JavaScript. If the data requires 
#      JavaScript to even exist, requests will just see a blank page.
#    - Waiting: Irrelevant. The moment you get the response back, you have 100% of the data.
# 
# 2. The Selenium Mindset: The "Puppeteer"
#    - Mental Model: You are literally remote-controlling a ghost user sitting at a keyboard. 
#      You don't just "download text"; you open browsers, navigate pages, and wait for the 
#      screen to paint. 
#    - Patience is Key: Because you are driving a real browser rendering a real website, 
#      things take time. Your primary enemy is not parsing HTML, it is timing. If your code 
#      tries to grab data a millisecond before the page's JavaScript places it on the screen, 
#      your scraper will crash. Therefore, Explicit Waiting becomes the most critical skill.
#    - Capabilities vs. Cost: You can click, scroll, login, and scrape the most complex, 
#      dynamically-loaded Sites (React, Vue, etc.) seamlessly. The trade-off is speed and 
#      resources. It takes vastly more RAM and CPU than requests.
