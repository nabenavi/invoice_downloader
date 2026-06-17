# nikkei.py

import os
from datetime import date
from dateutil.relativedelta import relativedelta

from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from smbc import save_current_page_as_pdf


load_dotenv()

NIKKEI_ID = os.getenv("NIKKEI_ID")
NIKKEI_PASSWORD = os.getenv("NIKKEI_PASSWORD")


def calc_target_ym(year, month):
    target = date(year, month, 1) - relativedelta(months=1)
    return f"{target.year}{target.month:02d}"


def click_next(driver):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="submit"]'))
    ).click()

def nikkei_login(driver):
    # ID入力欄がある場合
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.clear()
        email_input.send_keys(NIKKEI_ID)
        print("日経IDを入力しました。")
    except Exception:
        print("ID入力欄なし。既にID選択済みとして進みます。")

    click_next(driver)

    password_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_input.clear()
    password_input.send_keys(NIKKEI_PASSWORD)
    print("日経パスワードを入力しました。")

    click_next(driver)

def nikkei_download(driver, year, month, base_dir):
    target_ym = calc_target_ym(year, month)

    driver.get("https://id.nikkei.com/account/payments/histories")

    # ログイン画面に飛ばされた場合だけログイン
    if "login" in driver.current_url:
        nikkei_login(driver)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "payment-date"))
    )

    select = Select(driver.find_element(By.ID, "payment-date"))
    select.select_by_value(target_ym)

    # 明細ボタンを押す
    detail_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//span[contains(text(), "明細")]')
        )
    )
    driver.execute_script("arguments[0].click();", detail_button)

    # 明細ページへ遷移
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="button-print"]'))
    )

    pdf_path = base_dir / f"nikkei{target_ym}領収書.pdf"
    save_current_page_as_pdf(driver, pdf_path)