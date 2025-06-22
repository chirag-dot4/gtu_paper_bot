from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def fetch_pdf(course, session, subject_code):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Needed on Render

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://gtu.ac.in/Download1.aspx")
        time.sleep(3)

        # Select session (triggers postback)
        Select(driver.find_element(By.ID, "ddlSession")).select_by_visible_text(session)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ddlCourse")))

        # Select course after page reload
        Select(driver.find_element(By.ID, "ddlCourse")).select_by_visible_text(course)
        time.sleep(1)

        # Enter subject code and search
        driver.find_element(By.ID, "txtSearch").send_keys(subject_code)
        driver.find_element(By.ID, "btnSearch").click()
        time.sleep(3)

        # Extract download link
        link = driver.find_element(By.XPATH, "//table[@id='grdDownloads']//a").get_attribute("href")
        response = requests.get(link)

        # Save PDF
        file_path = f"{subject_code}.pdf"
        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Error in fetch_pdf():", e)
        return None

    finally:
        driver.quit()
