# auto_dl.py

from datetime import date
from pathlib import Path
import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from smbc import smbc_download
from openai import openai_download
from adobe import adobe_download
from nikkei import nikkei_download


load_dotenv()
today = date.today()

YEAR = today.year
MONTH = today.month
YM = f"{YEAR}{MONTH:02d}"

INVOICE_BASE_DIR = os.getenv("INVOICE_BASE_DIR")
if INVOICE_BASE_DIR:
    SAVE_PARENT_DIR = Path(INVOICE_BASE_DIR)
else:
    SAVE_PARENT_DIR = Path.home() / "Documents"

BASE_DIR = SAVE_PARENT_DIR / f"{MONTH}月"
BASE_DIR.mkdir(parents=True, exist_ok=True)

DOWNLOAD_DIR = Path.home() / "Downloads"

def make_driver():
    options = Options()

    profile_dir = Path(__file__).parent / "chrome_profile"
    profile_dir.mkdir(exist_ok=True)

    options.add_argument(
        f"--user-data-dir={profile_dir}"
    )

    driver = webdriver.Chrome(options=options)

    driver.maximize_window()
    return driver


def main():
    driver = make_driver()

    smbc_download(driver, YEAR, MONTH, BASE_DIR)
    openai_download(driver, YEAR, MONTH, BASE_DIR, DOWNLOAD_DIR)
    adobe_download(driver, YEAR, MONTH, BASE_DIR, DOWNLOAD_DIR)
    nikkei_download(driver, YEAR, MONTH, BASE_DIR)
    input("確認したら Enter: ")
    driver.quit()


if __name__ == "__main__":
    main()