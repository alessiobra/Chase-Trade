from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import json
import os
import re
import math
import certifi 

#os.environ['SSL_CERT_FILE'] = certifi.where()

# Define the user data directory
user_data_dir = os.path.join(os.getcwd(), "selenium_profile")
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=selenium")  # Set a custom user data directory
options.add_argument("--profile-directory=12")  # Specify the profile directory (replace 'Default' with your profile name)
options.add_argument(f"--user-data-dir={user_data_dir}")  # Set a custom user data directory
#options.binary_location = "/Users/alessiob/Desktop/Google Chrome/Contents/MacOS/Google Chrome"  # Update the path to the correct location
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"  # Update the path if Chrome is installed in a different location
driver = webdriver.Chrome(options=options)

username = ""
password = ""
stock_tickers = ["AAPL", "PYPL"]
stock_action = "buy"
shares = 1
account_numbers = []
ah = False # set to true if buying/selling in after hours trading

driver.get("https://secure.chase.com/web/auth/dashboard#/dashboard/index/index")

wait = WebDriverWait(driver, 120)

wait.until(EC.url_to_be("https://secure.chase.com/web/auth/dashboard#/dashboard/overview"))

wait = WebDriverWait(driver, 20)

def get_ask():
    # Locate the ask price element
    # Wait for the specific element containing the ask price to be present and visible
    ask_price_element = wait.until(
        EC.visibility_of_element_located((By.XPATH, '//dt[text()="Ask x size"]/following-sibling::dd[@class="mds-text-right"]')))

    # Extract the text from the element after ensuring it is fully loaded
    ask_price_text = ask_price_element.get_attribute("innerText").strip()

    print(f"Extracted ask price text: '{ask_price_text}'")
    
    # Extract the price from the text and convert it to a float
    ask_price = float(ask_price_text.split(' ')[0].replace('$', ''))  # This splits the text and takes the first part which is the price
    # Round the ask price
    rounded_ask_price = (math.ceil(ask_price * 100) / 100) + .01
    return rounded_ask_price

def get_bid():
    # Locate the ask price element
    # Wait for the specific element containing the ask price to be present and visible
    bid_price_element = wait.until(
        EC.visibility_of_element_located((By.XPATH, '//dt[text()="Bid x size"]/following-sibling::dd[@class="mds-text-right"]')))

    # Extract the text from the element after ensuring it is fully loaded
    bid_price_text = bid_price_element.get_attribute("innerText").strip()

    print(f"Extracted ask price text: '{bid_price_text}'")
    
    # Extract the price from the text and convert it to a float
    bid_price = float(bid_price_text.split(' ')[0].replace('$', ''))  # This splits the text and takes the first part which is the price
    # Round the ask price
    rounded_bid_price = math.floor(bid_price * 100) / 100
    return rounded_bid_price

def buy():
    for number in account_numbers:
        count = 0
        for stock_ticker in stock_tickers:
            time.sleep(3)
            driver.get(f"https://secure.chase.com/web/auth/dashboard#/dashboard/trade/equity/entry;ai={number};sym=")
            
            if count > 0:
                driver.refresh()
            
            count += 1

            stock_input = wait.until(EC.presence_of_element_located((By.ID, "symbolLookupInput")))
            stock_input.click()
            time.sleep(1)
            stock_input.send_keys(stock_ticker)
            time.sleep(2)
            stock_input.send_keys(Keys.RETURN)

            order_type = wait.until(EC.presence_of_element_located((By.ID, "orderTypeDropdownList"))) # timeout
            order_type.click()
            
            buy = wait.until(EC.presence_of_element_located((By.ID, "orderAction-segmentedButtonInput-0")))
            driver.execute_script("arguments[0].click();", buy)

            if ah:
                limit = wait.until(EC.presence_of_element_located((By.XPATH, "//mds-select-option[@data-testid='selectedOption_LIMIT']")))
                limit.click()

                enter_limit = wait.until(EC.presence_of_element_located((By.ID, "orderLimitPrice")))
                time.sleep(2)
                enter_limit.send_keys(get_ask())

                radio_group = wait.until(EC.presence_of_element_located((By.XPATH, '//mds-radio-group[@data-testid="timeInForceRadioGroup"]')))
                shadow_root = driver.execute_script('return arguments[0].shadowRoot', radio_group)
                day_radio_button = shadow_root.find_element(By.CSS_SELECTOR, 'input#timeInForceRadioGroup-input-0')
                day_radio_button.click()
            else:
                market_buy = wait.until(EC.presence_of_element_located((By.XPATH, "//mds-select-option[@data-testid='selectedOption_MARKET']")))
                market_buy.click()

            order_details_display = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'mds-text-input#orderQuantity')))
            shadow_root = driver.execute_script('return arguments[0].shadowRoot', order_details_display)
            qty = shadow_root.find_element(By.CSS_SELECTOR, 'input#orderQuantity-input')
            qty.click()
            qty.send_keys(shares)

            preview = wait.until(EC.presence_of_element_located((By.ID, "previewButton")))
            preview.click()
            
            if ah:
                accept = wait.until(EC.presence_of_element_located((By.ID, "acceptWarningsButtonContainer")))
                driver.execute_script("arguments[0].click();", accept)

                acc = accept.find_element(By.ID, "acceptWarningsButton")
                driver.execute_script("arguments[0].click();", acc)

                place_order = wait.until(EC.presence_of_element_located((By.XPATH, "//mds-button[@data-testid='submitButton']")))
                driver.execute_script("arguments[0].click();", place_order)

                print(f"{stock_ticker} purchased on account {number}!")
            else:
                place_order = wait.until(EC.presence_of_element_located((By.XPATH, "//mds-button[@data-testid='submitButton']")))
                driver.execute_script("arguments[0].click();", place_order)

                print(f"{stock_ticker} purchased on account {number}!")

def sell():
    for number in account_numbers:
        count = 0
        for stock_ticker in stock_tickers:
            time.sleep(3)
            driver.get(f"https://secure.chase.com/web/auth/dashboard#/dashboard/trade/equity/entry;ai={number};sym=")
            
            if count > 0:
                driver.refresh()
            
            count += 1

            stock_input = wait.until(EC.presence_of_element_located((By.ID, "symbolLookupInput")))
            stock_input.click()
            time.sleep(1)
            stock_input.send_keys(stock_ticker)
            time.sleep(2)
            stock_input.send_keys(Keys.RETURN)

            sell_all = wait.until(EC.presence_of_element_located((By.ID, "orderAction-segmentedButtonInput-2")))
            sell_all.click()

            order_type = wait.until(EC.presence_of_element_located((By.ID, "orderTypeDropdownList"))) # timeout
            order_type.click()

            market = wait.until(EC.presence_of_element_located((By.XPATH, "//mds-select-option[@data-testid='selectedOption_MARKET']")))
            market.click()

            preview = wait.until(EC.presence_of_element_located((By.ID, "previewButton")))
            preview.click()

            place_order = wait.until(EC.presence_of_element_located((By.XPATH, "//mds-button[@data-testid='submitButton']")))
            driver.execute_script("arguments[0].click();", place_order)

            print(f"{stock_ticker} sold on account {number}!")

if stock_action == "buy":
    buy()
else:
    sell()


