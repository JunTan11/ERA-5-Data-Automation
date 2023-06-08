from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import os
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pyautogui
from selenium.webdriver.chrome.options import Options

# changable data
download_directory = "your directory"
webdriver_path = 'your path'
my_email = "your email"
my_password = "your password"
download_directory = "your directory"

options = Options()
options.add_experimental_option('prefs', {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False, 
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})

# Set up WebDriver
driver = webdriver.Chrome(options=options, executable_path=webdriver_path)

# the website
driver.get("https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=form")

# Wait for the page to load
time.sleep(2)
wait = WebDriverWait(driver, 4)

# full screen
driver.maximize_window()

# Clicking 'I agree' to accept cookies
accept_cookie = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'agree-button')))
accept_cookie.click()

# Select the login button
login_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Login/register')]")))
login_link.click()

# fill in my email address
input_field = wait.until(EC.visibility_of_element_located((By.ID, "edit-name")))
text_to_enter = my_email
input_field.send_keys(text_to_enter)

# fill in my password
password_input = wait.until(EC.visibility_of_element_located((By.ID, "edit-pass")))
password_to_enter = my_password
password_input.send_keys(password_to_enter)

# click on the login button
button = wait.until(EC.element_to_be_clickable((By.ID, "edit-submit")))
button.click()

# Select the parameter (2m dewpoint temperature)
temperature_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '2m dewpoint temperature')]/ancestor::div[@class='StringListWidgetCheckboxLabel']/preceding-sibling::input")))
temperature_element.click()

# Dictionary mapping month values to month names
months = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

# scroll down slightly
driver.execute_script("window.scrollTo(0, 2600)") 

# Select all of the days
# selecting the physical point on the screen, since the script was unable to locate the correct button
# Move the mouse cursor to the desired coordinates, varies in different screen sizes
pyautogui.moveTo(x=1305, y=655, duration=0.4)

# Click at the current mouse position
pyautogui.click()

# Wait for a moment
time.sleep(2)

# Move the mouse cursor to the second set of coordinates
pyautogui.moveTo(x=1305, y=969, duration=0.4)

# Click at the current mouse position
pyautogui.click()

# accepting the terms (if applicable)
try:
    accept_button = driver.find_element_by_xpath("//input[@value='Accept terms']")
    accept_button.click()
except NoSuchElementException:
    pass

# Click the sub-region extraction option
sub_region_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.FrameWidgetRadio[value='7']")))
sub_region_option.click()

# Select the correct format
format_radio_button = driver.find_element_by_xpath("//input[@value='netcdf.zip']")
format_radio_button.click()

# Iterate over the years and months
for year in range(1950, 1951):  # replace end year with the end year + 1
    # Select the year
    year_radio_button = driver.find_element_by_xpath(f"//input[@value='{year}']")
    year_radio_button.click()

    for month in months:
        # Select the month
        month_radio_button = driver.find_element_by_xpath(f"//input[@value='{month}']")
        month_radio_button.click()

        # Fill out the correct parameters for the sub-region extraction
        north_input = driver.find_element_by_name('n')
        north_input.clear()
        north_input.send_keys('30')
        east_input = driver.find_element_by_name('e')
        east_input.clear()
        east_input.send_keys('155')
        west_input = driver.find_element_by_name('w')
        west_input.clear()
        west_input.send_keys('85')
        south_input = driver.find_element_by_name('s')
        south_input.clear()
        south_input.send_keys('-15')

        # Submit the form
        button = driver.find_element_by_xpath("//input[@value='Submit Form']")
        button.click()

        # close the pop-up (if present)
        time.sleep(1)
        try:
            close_button = driver.find_element_by_class_name("close-icon")
            close_button.click()
        except NoSuchElementException:
            pass
        
        # Preparing to click on the download button
        button_xpath = "//a[contains(@class, 'btn-success') and contains(text(), 'Download')]"
        # Wait
        wait_time = 10
        button = None

        # Wait until the button is clickable or the wait time is exceeded
        try:
            button = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        except:
            pass

        # Click the button if it is found
        if button is not None:
            button.click()


        # Rename and move the file
        for filename in os.listdir(download_directory):
            if filename.endswith(".zip"):
                old_path = os.path.join(download_directory, filename)
                new_path = os.path.join(download_directory, f"{year}_{month}.zip")
                shutil.move(old_path, new_path)

        # delete the file from the list of downloads on the site
        checkmark = driver.find_element_by_xpath("//span[contains(@class, 'mark-button') and contains(@class, 'fa-square-o')]")
        checkmark.click()
        delete_button = driver.find_element_by_xpath("//button[contains(text(), 'Delete selected')]")
        delete_button.click()

        # clicking on the confirm button
        time.sleep(1.5)
        button_xpath = "//button[contains(@class, 'btn-primary') and contains(text(), 'Delete')]"
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()

        # return to the previous page
        driver.back()

