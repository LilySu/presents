from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_to_amazon(email, password):
    # Initialize the webdriver (Chrome in this example)
    driver = webdriver.Chrome()
    
    # Navigate to Amazon's login page
    driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&")
    
    try:
        # Wait for the email input field to be visible and enter the email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(email)
        
        # Click the 'Continue' button
        continue_button = driver.find_element(By.ID, "continue")
        continue_button.click()
        
        # Wait for the password input field to be visible and enter the password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(password)
        
        # Click the 'Sign-In' button
        sign_in_button = driver.find_element(By.ID, "signInSubmit")
        sign_in_button.click()
        
        # Wait for the login process to complete (you may need to adjust this based on Amazon's behavior)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-link-accountList"))
        )
        
        print("Successfully logged in!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Keep the browser open for 5 seconds to see the result
        import time
        time.sleep(5)
        
        # Close the browser
        driver.quit()

# Usage example
login_to_amazon("your_email@example.com", "your_password")