#!/usr/bin/env python3
"""
Décompose le login Selenium réel en phases, avec un polling fin (50 ms)
pour dater l'arrivée effective du token dans localStorage.

Usage : python bench/profile_login.py
"""

import importlib.util
import json
import pathlib
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "exporter", ROOT / "naviki-gpx-exporter.py"
)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

OAUTH_URL = (
    "https://www.naviki.org/oauth2/auth?lang=fr"
    "&redirect_uri=https://www.naviki.org/fr/naviki/"
    "single-pages/loading//mobile.html&client_id=web"
    "&scope=way,profile,contest&response_type=code"
)


def main():
    env = exporter.load_env_file()
    marks = {}
    t0 = time.perf_counter()
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    marks["firefox_started"] = time.perf_counter() - t0
    try:
        driver.get(OAUTH_URL)
        marks["oauth_page_loaded"] = time.perf_counter() - t0
        user = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user.send_keys(env["NAVIKI_USERNAME"])
        driver.find_element(By.NAME, "password").send_keys(env["NAVIKI_PASSWORD"])
        buttons = driver.find_elements(
            By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
        )
        if buttons:
            buttons[0].click()
        else:
            driver.find_element(By.NAME, "password").submit()
        marks["submitted"] = time.perf_counter() - t0
        while time.perf_counter() - t0 < 30:
            if driver.execute_script("return localStorage.getItem('_n_a_at');"):
                marks["token_available"] = time.perf_counter() - t0
                break
            time.sleep(0.05)
    finally:
        t = time.perf_counter()
        driver.quit()
        marks["quit_s"] = time.perf_counter() - t
    print(json.dumps({k: round(v, 3) for k, v in marks.items()}))


if __name__ == "__main__":
    main()
