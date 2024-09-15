from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
import time
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Access the API key
email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD")

def login_to_amazon(email: str, password: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Keep this False for debugging
        page = browser.new_page()

        try:
            # Navigate to Amazon's login page
            try:
                page.goto('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0', wait_until='networkidle', timeout=60000)
                time.sleep(4)  # Wait for 2 seconds after page load
            except PlaywrightTimeoutError:
                raise Exception("Timeout while loading Amazon login page. Check your internet connection.")

            # Wait for and fill email field
            try:
                email_field = page.wait_for_selector('#ap_email', state='visible', timeout=60000)
                email_field.fill(email)
                print("Email field filled successfully")
                time.sleep(3)  # Wait for 1 second after filling email
            except PlaywrightTimeoutError:
                raise Exception("Email field not found or not interactable within 60 seconds.")

            # Click continue
            try:
                continue_button = page.wait_for_selector('#continue', state='visible', timeout=30000)
                continue_button.click()
                print("Clicked continue button")
                time.sleep(4)  # Wait for 2 seconds after clicking continue
            except PlaywrightTimeoutError:
                raise Exception("Continue button not found or not clickable within 30 seconds.")

            # Wait for and fill password field
            try:
                password_field = page.wait_for_selector('#ap_password', state='visible', timeout=30000)
                password_field.fill(password)
                print("Password field filled successfully")
                time.sleep(3)  # Wait for 1 second after filling password
            except PlaywrightTimeoutError:
                raise Exception("Password field not found or not interactable within 30 seconds.")

            # Click submit
            try:
                sign_in_button = page.wait_for_selector('#signInSubmit', state='visible', timeout=30000)
                sign_in_button.click()
                print("Clicked sign in button")
                time.sleep(4)  # Wait for 3 seconds after clicking sign in
            except PlaywrightTimeoutError:
                raise Exception("Sign in button not found or not clickable within 30 seconds.")

            # Wait for navigation to complete
            try:
                page.wait_for_load_state('networkidle', timeout=60000)
            except PlaywrightTimeoutError:
                print("Warning: Page took too long to load after clicking sign in.")

            # Check if login was successful
            if page.url.startswith('https://www.amazon.com/'):
                print('Login successful')
                time.sleep(4)  # Wait for 3 seconds after successful login
            else:
                print('Login may have failed. Current URL:', page.url)
                # Check for common error messages
                error_message = page.locator('.a-alert-content').inner_text()
                if error_message:
                    print(f"Error message found: {error_message}")

            # For debugging: save a screenshot
            page.screenshot(path='amazon_login_result.png')

        except Exception as e:
            print(f'An error occurred: {e}')
            # For debugging: save a screenshot when an error occurs
            page.screenshot(path='amazon_login_error.png')
            # Print the current URL when an error occurs
            print(f"Current URL when error occurred: {page.url}")
            # Print the page content for further debugging
            print("Page content:")
            print(page.content())

        # Keep the browser open
        input("Press Enter to close the browser...")
        browser.close()

if __name__ == "__main__":
    if not email or not password:
        print("Error: EMAIL or PASSWORD environment variables are not set.")
        sys.exit(1)
    
    login_to_amazon(email, password)