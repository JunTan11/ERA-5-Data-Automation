from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import os
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import pyautogui
from selenium.webdriver.chrome.options import Options

# changeable data
download_directory = "download directory"
webdriver_path = 'webdriver path'
my_email = "email"
my_password = "password"

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

# Select the parameter (2m temperature)
temperature_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '2m temperature')]/ancestor::div[@class='StringListWidgetCheckboxLabel']/preceding-sibling::input")))
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

# Wait
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
        month_radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@value='{month}']")))
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
        
        # clicking the download button
        time.sleep(380) # change this to 380 once testing has been completed
        pyautogui.moveTo(x=1715, y=930, duration=0.4)
        pyautogui.click()

        # wait for file to be downloaded
        time.sleep(370)

        # Get the list of all .zip files in the directory
        zip_files = [f for f in os.listdir(download_directory) if f.endswith(".zip")]

        # Find the most recently downloaded .zip file
        latest_file = max(zip_files, key=lambda f: os.path.getmtime(os.path.join(download_directory, f)))

        # Rename the file
        old_path = os.path.join(download_directory, latest_file)
        new_path = os.path.join(download_directory, f"{year}_{month}.zip")
        os.rename(old_path, new_path)

        # # delete online downloaded list of data (not working)
        # # delete the file from the list of downloads on the site
        # time.sleep(10)
        # checkmark = driver.find_element_by_xpath("//span[contains(@class, 'mark-button') and contains(@class, 'fa-square-o')]")
        # checkmark.click()
        # delete_button = driver.find_element_by_xpath("//button[contains(text(), 'Delete selected')]")
        # delete_button.click()

        # # click on the delete button on the confirmation page
        # time.sleep(3)
        # element = driver.find_element_by_xpath("//span[contains(@class, 'mark-button') and contains(@class, 'fa-square-o')]")
        # driver.execute_script("arguments[0].click();", element)


        # return to the previous page
        driver.back()

