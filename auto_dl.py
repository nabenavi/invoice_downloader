# auto_dl.py

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from smbc import smbc_download


YEAR = 2026
MONTH = 6
YM = f"{YEAR}{MONTH:02d}"

BASE_DIR = Path.home() / "Documents" / "請求書領収書" / YM
BASE_DIR.mkdir(parents=True, exist_ok=True)


def make_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def main():
    driver = make_driver()

    smbc_download(driver, YEAR, MONTH, BASE_DIR)

    input("確認したら Enter: ")
    driver.quit()


if __name__ == "__main__":
    main()