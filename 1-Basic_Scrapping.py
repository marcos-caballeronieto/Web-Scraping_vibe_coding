# ==========================================
# Phase 1: Imports - Bringing in our Tools
# ==========================================

# WHY DO WE NEED 'requests'?
# The internet works by computers sending "requests" to other computers (servers) 
# and getting "responses" back. Browsers like Chrome or Firefox do this for you automatically.
# Since we are writing a script, we need a way for our Python code to act like a browser
# and ask the server at 'quotes.toscrape.com' for its web page data. The 'requests' 
# library simplifies this process of sending HTTP requests and receiving the HTML response.
import requests

# WHY DO WE NEED 'BeautifulSoup'?
# When 'requests' gets the web page, it just gives us a massive, raw string of HTML text. 
# HTML is structured with tags (like <div>, <span>, <h1>), but raw text is very hard for 
# Python to search through reliably. BeautifulSoup takes that raw HTML string and builds a 
# structured tree out of it behind the scenes. It gives us simple tools to say, 
# "Find me all the <span> tags with the class 'text'," instead of us having to write 
# complex text-searching rules ourselves.
from bs4 import BeautifulSoup


def scrape_quotes():
    # The URL (web address) of the site we want to scrape.
    url = "http://quotes.toscrape.com/"

    # ==========================================
    # Phase 2: Fetching the Web Page
    # ==========================================
    
    # We use requests.get() to literally say: "Go to this URL and GET the data."
    # The result is stored in the 'response' variable.
    print(f"Fetching data from: {url}")
    response = requests.get(url)

    # WHY CHECK THE STATUS CODE AND USE raise_for_status()?
    # When a server replies, it includes a "status code" (like 200 for "OK", 
    # 404 for "Not Found", or 500 for "Server Error"). 
    # If we don't check this, our script might try to read an error page (like a 404 page)
    # thinking it's the real content, which will cause our script to crash later on in confusing ways.
    # raise_for_status() is a handy function that says: "If the status code was anything 
    # other than a success (200-series), stop the program immediately and throw an error."
    # It protects us from trying to scrape broken or missing pages.
    response.raise_for_status()

    # ==========================================
    # Phase 3: Parsing the HTML Data
    # ==========================================
    
    # WHY PASS 'html.parser'?
    # BeautifulSoup can understand different types of markup languages (like XML or HTML).
    # Furthermore, there are different "parsers" (engines) it can use to make sense of the HTML.
    # 'html.parser' is built into Python, meaning we don't have to install any extra tools 
    # to use it. By passing 'html.parser', we are explicitly telling BeautifulSoup: 
    # "The text I am giving you is standard HTML, please use Python's built-in engine to 
    # structure it so I can search it."
    # 'response.text' contains the raw HTML string we got from the website.
    soup = BeautifulSoup(response.text, 'html.parser')

    # ==========================================
    # Phase 4: Selecting the Data We Want
    # ==========================================
    
    # WHY AND HOW DO WE FIND SPECIFIC ELEMENTS?
    # Web pages are visually organized using HTML tags and "classes". 
    # If you go to quotes.toscrape.com, right-click a quote, and select "Inspect", 
    # you'll see the HTML behind the scenes.
    # You will notice that every single quote on the page is wrapped in a <div> tag 
    # that looks like this: <div class="quote">...</div>
    # 
    # We use soup.find_all('div', class_='quote') to tell BeautifulSoup:
    # "Look through the entire HTML tree. Find every single <div> tag that has the class 'quote'. 
    # Give them all back to me as a list."
    # (Note: we use 'class_' with an underscore because 'class' is a reserved word in Python).
    quote_elements = soup.find_all('div', class_='quote')

    print(f"Successfully found {len(quote_elements)} quotes on the page.\n")

    # Now we loop through each specific quote block we found.
    for element in quote_elements:
        
        # Inside each <div class="quote">, the actual text of the quote is hiding 
        # inside a <span> tag with the class 'text': <span class="text">"The quote..."</span>
        # We use `.find()` here instead of `.find_all()` because we only want the FIRST 
        # matching item inside this specific block, not a list.
        # We add `.text` at the end to say: "Don't give me the HTML tags (<span...>), 
        # just give me the human-readable text inside those tags."
        text = element.find('span', class_='text').text
        
        # Similarly, the author's name is inside a <small> tag with the class 'author'.
        author = element.find('small', class_='author').text
        
        # Finally, we print out the extracted, clean data.
        print(f"Quote: {text}")
        print(f"Author: {author}")
        print("-" * 40)

# This is the standard way to run a Python script directly.
if __name__ == "__main__":
    scrape_quotes()

# ==========================================
# Best Practices for Beginners Scraping the Web
# ==========================================
# 
# 1. Check `robots.txt` First: Before scraping a real website (like `example.com`), 
#    check `example.com/robots.txt`. This is a file where website owners state the 
#    rules for automated bots. It tells you which pages you are allowed to scrape 
#    and which are strictly off-limits.
# 
# 2. Be Polite (Rate Limiting): Computers can click links much faster than humans. 
#    If your script requests 1,000 pages a second, you could accidentally overwhelm 
#    the website's server. Always use `time.sleep()` in your loops to pause for a 
#    second or two between requests.
# 
# 3. Inspect the Page First: Always open your web browser, right-click the data you 
#    want, and hit "Inspect" (or "Inspect Element"). You need to understand the HTML 
#    structure (the tags and classes) before you can write your BeautifulSoup code.
# 
# 4. Identify Yourself (User-Agent): By default, the `requests` library announces 
#    itself as a generic python library. Some websites block this. Pass a custom 
#    "User-Agent" header (e.g., `requests.get(url, headers={'User-Agent': 'Mozilla/5.0 ...'})`) 
#    to look like a normal web browser.
# 
# 5. Fail Gracefully: Web scraping is fragile. Websites redesign their HTML all the 
#    time. Elements you rely on might be missing. If `.find()` doesn't find anything, 
#    it returns `None`. Write code to handle these cases (like try/except blocks).
