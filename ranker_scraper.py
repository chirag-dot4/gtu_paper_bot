import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://gturanker.org"

def get_courses():
    r = requests.get(f"{BASE_URL}/papers/")
    soup = BeautifulSoup(r.text, "html.parser")
    course_links = soup.select(".btn.btn-dark")
    return [(a.text.strip(), BASE_URL + a["href"]) for a in course_links]

def get_next_level(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    buttons = soup.select(".btn.btn-primary, .btn.btn-secondary")
    if buttons:
        return [(btn.text.strip(), BASE_URL + btn["href"]) for btn in buttons]
    else:
        # final page with table (paper links)
        table_links = soup.select("table a.btn")
        if not table_links:
            return None
        return [(a.text.strip(), BASE_URL + a["href"]) for a in table_links]

def get_pdf(link):
    try:
        r = requests.get(link, stream=True)
        filename = link.split("/")[-1]
        path = f"/tmp/{filename}"
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return path
    except Exception as e:
        print("Download failed:", e)
        return None
