from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
import time
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import json
from datetime import datetime

def find_dotenv_path():
    current_dir = Path(__file__).resolve().parent
    shop_presents_dir = current_dir
    while shop_presents_dir.name != 'shop_presents' or 'src' in shop_presents_dir.parts:
        shop_presents_dir = shop_presents_dir.parent
        if shop_presents_dir == shop_presents_dir.parent:  # reached root
            raise Exception("Could not find the shop_presents directory.")
    return shop_presents_dir.parent / '.env'

# Find and load the .env file
dotenv_path = find_dotenv_path()
load_dotenv(dotenv_path)

# Get credentials from environment variables
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def login_to_amazon(playwright):
    browser = playwright.chromium.launch(headless=False)  # Keep this False for debugging
    page = browser.new_page()

    try:
        # Navigate to Amazon's login page
        page.goto('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0', wait_until='networkidle', timeout=60000)
        time.sleep(4)  # Wait for 4 seconds after page load

        # Fill email field
        email_field = page.wait_for_selector('#ap_email', state='visible', timeout=60000)
        email_field.fill(email)
        print("Email field filled successfully")
        time.sleep(3)  # Wait for 3 seconds after filling email

        # Click continue
        continue_button = page.wait_for_selector('#continue', state='visible', timeout=30000)
        continue_button.click()
        print("Clicked continue button")
        time.sleep(4)  # Wait for 4 seconds after clicking continue

        # Fill password field
        password_field = page.wait_for_selector('#ap_password', state='visible', timeout=30000)
        password_field.fill(password)
        print("Password field filled successfully")
        time.sleep(3)  # Wait for 3 seconds after filling password

        # Click submit
        sign_in_button = page.wait_for_selector('#signInSubmit', state='visible', timeout=30000)
        sign_in_button.click()
        print("Clicked sign in button")
        time.sleep(4)  # Wait for 4 seconds after clicking sign in

        # Wait for navigation to complete
        page.wait_for_load_state('networkidle', timeout=60000)

        # Check if login was successful
        if page.url.startswith('https://www.amazon.com/'):
            print('Login successful')
            return browser, page
        else:
            print('Login may have failed. Current URL:', page.url)
            return None, None

    except Exception as e:
        print(f'An error occurred during login: {e}')
        page.screenshot(path='login_error.png')
        print(f"Login error screenshot saved as 'login_error.png'")
        return None, None

def search_and_extract_results(page, search_term):
    try:
        # Wait for 5 seconds before starting the search
        time.sleep(5)

        # Focus on the search bar
        search_bar = page.wait_for_selector('#twotabsearchtextbox', state='visible', timeout=60000)
        search_bar.click()

        # Type the search query
        search_bar.fill(search_term)

        # Press Enter to search
        page.keyboard.press('Enter')

        # Wait for search results to start loading
        page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=60000)

        # Scroll down the page to load more results
        for _ in range(3):  # Scroll 3 times
            page.evaluate('window.scrollBy(0, window.innerHeight)')
            time.sleep(2)

        # Extract search results
        results = page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('div[data-component-type="s-search-result"]'));
            return items.slice(0, 10).map(item => {  // Limit to first 10 results
                const titleElement = item.querySelector('h2 a span');
                const linkElement = item.querySelector('h2 a');
                const priceElement = item.querySelector('.a-price-whole');
                const ratingElement = item.querySelector('.a-icon-star-small .a-icon-alt');
                const sponsoredElement = item.querySelector('.s-sponsored-label-info-icon');
                const purchaseInfoElement = item.querySelector('.a-size-base.a-color-secondary');
                
                let purchaseInfo = '';
                if (purchaseInfoElement) {
                    const text = purchaseInfoElement.innerText;
                    const match = text.match(/(\d+,?\d*) bought in past month/);
                    if (match) {
                        purchaseInfo = match[0];
                    }
                }
                
                return {
                    title: titleElement ? titleElement.innerText : 'N/A',
                    product_url: linkElement ? 'https://www.amazon.com' + linkElement.getAttribute('href') : 'N/A',
                    price: priceElement ? priceElement.innerText : 'N/A',
                    rating: ratingElement ? ratingElement.innerText : 'N/A',
                    sponsored: sponsoredElement ? 'Yes' : 'No',
                    purchase_info: purchaseInfo || 'N/A'
                };
            });
        }''')

        # Capture current URL and page title
        current_url = page.url
        page_title = page.title()

        return results, current_url, page_title

    except Exception as e:
        print(f"An error occurred during search and extraction: {e}")
        page.screenshot(path='search_error.png')
        print(f"Search error screenshot saved as 'search_error.png'")
        return None, page.url, page.title()
    
def create_json_file(search_term, results, current_url, page_title):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_minutes = now.hour * 60 + now.minute

    data = {
        "search_term": search_term,
        "date": date_str,
        "time_minutes": time_minutes,
        "current_url": current_url,
        "page_title": page_title,
        "results": results
    }

    filename = f"search_results_{date_str}_{time_minutes}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"JSON file '{filename}' has been created in the local directory.")

if __name__ == "__main__":
    if not email or not password:
        print("Error: EMAIL or PASSWORD environment variables are not set.")
        sys.exit(1)
    
    search_term = "wireless mouse"  # You can change this to any search term you want
    
    with sync_playwright() as playwright:
        browser, page = login_to_amazon(playwright)
        if browser and page:
            try:
                results, current_url, page_title = search_and_extract_results(page, search_term)
                
                print(f"\nCurrent URL: {current_url}")
                print(f"Page Title: {page_title}\n")
                
                if results:
                    print(f"--- Search Results for '{search_term}' ---\n")
                    for i, result in enumerate(results, 1):
                        print(f"Result {i}:")
                        print(f"Title: {result.get('title', 'N/A')}")
                        print(f"Product URL: {result.get('product_url', 'N/A')}")
                        print(f"Price: {result.get('price', 'N/A')}")
                        print(f"Rating: {result.get('rating', 'N/A')}")
                        print(f"Sponsored: {result.get('sponsored', 'N/A')}")
                        print(f"Purchase Info: {result.get('purchase_info', 'N/A')}")
                        print("---")
                    
                    # Create JSON file
                    create_json_file(search_term, results, current_url, page_title)
                else:
                    print("No results found or an error occurred during extraction.")
                
            except Exception as e:
                print(f"An error occurred: {e}")
                page.screenshot(path='error.png')
                print(f"Error screenshot saved as 'error.png'")
            
            # Keep the browser open until user input
            input("Press Enter to close the browser...")
            browser.close()
        else:
            print("Login failed. Unable to perform search and extract results.")

# Update the create_json_file function to handle the new structure
def create_json_file(search_term, results, current_url, page_title):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_minutes = now.hour * 60 + now.minute

    data = {
        "search_term": search_term,
        "date": date_str,
        "time_minutes": time_minutes,
        "current_url": current_url,
        "page_title": page_title,
        "results": results
    }

    filename = f"search_results_{date_str}_{time_minutes}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"JSON file '{filename}' has been created in the local directory.")