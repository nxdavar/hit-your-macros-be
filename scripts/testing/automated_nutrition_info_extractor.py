from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)
import time
import os

# Setup the WebDriver (Assuming using Chrome)
driver = webdriver.Chrome()


# Function to take screenshot
def take_screenshot(driver, key):
    # Define the directory to save screenshots
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    # Path to save screenshot
    screenshot_path = os.path.join(screenshots_dir, f"{key}.png")

    # Check if screenshot already exists
    if not os.path.exists(screenshot_path):
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for: {key}")
    else:
        print(f"Screenshot already exists for: {key}")


# Set to store keys of taken screenshots
taken_screenshots = set()

# Visit the website
url = "https://www.bk.com/nutrition-explorer"  # Replace with the actual URL
driver.get(url)

try:
    while True:
        # Close pop-up if it exists
        # (Implement the logic to close the pop-up here if needed)

        # Find all div elements with the class 'css-175oi2r'
        divs = driver.find_elements(By.CSS_SELECTOR, "div.css-175oi2r")

        print('current divs: ', divs)

        for div in divs:
            # Find the h4 tag within the div to use its text as the key
            try:
                h4_tag = div.find_element(By.CSS_SELECTOR, "h4")
                key = h4_tag.text.strip()
            except NoSuchElementException:
                print("No h4 tag found in this div.")
                continue

            # Check if we already have a screenshot for this key
            if key not in taken_screenshots:
                # Click on all img tags within the div
                img_tags = div.find_elements(By.TAG_NAME, "img")
                for img in img_tags:
                    img.click()
                    time.sleep(1)  # Slight delay to allow any UI changes after click

                # Take a screenshot and save it using the key
                take_screenshot(driver, key)

                # Add key to the set of taken screenshots
                taken_screenshots.add(key)

        # Wait for 30 seconds before reloading the page
        time.sleep(30)
        driver.refresh()

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
