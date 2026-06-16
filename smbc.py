# smbc.py

import base64
from time import sleep
import os

from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()

SMBC_ID = os.getenv("SMBC_ID")
SMBC_PASSWORD = os.getenv("SMBC_PASSWORD")


def smbc_login(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.ID, "vp-view-VC8001001_RS0003_userid")
        )
    )

    driver.find_element(
        By.ID,
        "vp-view-VC8001001_RS0003_userid"
    ).send_keys(SMBC_ID)

    driver.find_element(
        By.ID,
        "vp-view-VC8001001_RS0003_password"
    ).send_keys(SMBC_PASSWORD)

    driver.find_element(
        By.CSS_SELECTOR,
        'input[value="ログイン"]'
    ).click()


def save_current_page_as_pdf(driver, pdf_path):
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})

    driver.execute_script("""
        document.querySelectorAll('div[style*="z-index: 999"]').forEach(e => {
            e.style.display = 'none';
        });
    """)

    sleep(1)

    result = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,
            "paperHeight": 11.69,
            "marginTop": 0.4,
            "marginBottom": 0.4,
            "marginLeft": 0.4,
            "marginRight": 0.4,
        }
    )

    pdf_data = base64.b64decode(result["data"])

    with open(pdf_path, "wb") as f:
        f.write(pdf_data)

    print(f"PDF保存しました: {pdf_path}")


def smbc_download(driver, year, month, base_dir):
    ym = f"{year}{month:02d}"

    url = f"https://www.smbc-card.com/memx/web_meisai/top/index.html?p01={ym}"
    driver.get(url)

    smbc_login(driver)

    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, 'div[style*="z-index: 999"]')
        )
    )

    before_handles = set(driver.window_handles)

    print_page_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.ID, "vp-view-VC0502-003_RS0001_U051510_1")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        print_page_button
    )

    sleep(1)

    driver.execute_script("arguments[0].click();", print_page_button)

    WebDriverWait(driver, 10).until(
        lambda d: len(d.window_handles) > len(before_handles)
    )

    new_handles = set(driver.window_handles) - before_handles
    driver.switch_to.window(new_handles.pop())

    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//a[contains(text(), "印刷する")]')
        )
    )

    sleep(2)

    pdf_path = base_dir / f"法人カード明細{ym}.pdf"
    save_current_page_as_pdf(driver, pdf_path)