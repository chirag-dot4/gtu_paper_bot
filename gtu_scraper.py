import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import requests

def fetch_pdf(course, session, subject_code):
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://gtu.ac.in/Download1.aspx")
        time.sleep(2)

        Select(driver.find_element(By.ID, "ddlSession")).select_by_visible_text(session)
        time.sleep(1)
        Select(driver.find_element(By.ID, "ddlCourse")).select_by_visible_text(course)
        time.sleep(1)
        driver.find_element(By.ID, "txtSearch").send_keys(subject_code)
        driver.find_element(By.ID, "btnSearch").click()
        time.sleep(2)

        link = driver.find_element(By.XPATH, "//table[@id='grdDownloads']//a").get_attribute("href")
        response = requests.get(link)
        file_path = f"{subject_code}.pdf"
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path

    except Exception as e:
        print("Error:", e)
        return None
    finally:
        driver.quit()
