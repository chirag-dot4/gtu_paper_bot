import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_paper(session, course, subject_code):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://gtu.ac.in/Download1.aspx")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "ddlSession")))
        driver.find_element(By.ID, "ddlSession").send_keys(session)
        driver.find_element(By.ID, "ddlCourse").send_keys(course)
        driver.find_element(By.ID, "txtSearch").send_keys(subject_code)
        driver.find_element(By.ID, "btnSearch").click()
        wait.until(EC.presence_of_element_located((By.ID, "gvData")))
        links = driver.find_element(By.ID, "gvData").find_elements(By.TAG_NAME, "a")
        if not links:
            return None
        href = links[0].get_attribute("href")
        filename = href.split("/")[-1]
        path = f"/tmp/{filename}"
        r = requests.get(href, headers={"User-Agent": "Mozilla/5.0"})
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()