import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://gturanker.org"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_courses():
    try:
        res = requests.get(f"{BASE_URL}/papers/", headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        course_links = soup.select(".btn.btn-dark")
        return [(a.text.strip(), BASE_URL + a["href"]) for a in course_links]
    except Exception as e:
        print("Error fetching courses:", e)
        return []

def get_next_level(url):
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # First: look for next-level buttons (semester, subjects, etc.)
        buttons = soup.select(".btn.btn-primary, .btn.btn-secondary")
        if buttons:
            return [(btn.text.strip(), BASE_URL + btn["href"]) for btn in buttons]

        # Otherwise: maybe this is the final page with PDF links
        table_links = soup.select("table a.btn")
        if table_links:
            return [(a.text.strip(), BASE_URL + a["href"]) for a in table_links]

        return None
    except Exception as e:
        print("Error in get_next_level:", e)
        return None

def get_pdf(link):
    try:
        r = requests.get(link, headers=headers, stream=True)
        filename = link.split("/")[-1]
        path = f"/tmp/{filename}"

        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        return path
    except Exception as e:
        print("Download failed:", e)
        return None
