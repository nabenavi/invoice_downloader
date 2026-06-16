# adobe.py

from time import sleep
import shutil

from selenium.webdriver.common.by import By

import time

def wait_for_download_pdf(download_dir):
    start_time = time.time()

    while True:
        sleep(1)

        if list(download_dir.glob("*.crdownload")):
            continue

        pdfs = list(download_dir.glob("*.pdf"))

        recent_pdfs = [
            p for p in pdfs
            if p.stat().st_mtime >= start_time
        ]

        if recent_pdfs:
            return max(recent_pdfs, key=lambda p: p.stat().st_mtime)


def click_download_button_and_rename(driver, button, download_dir, dest_path):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        button
    )

    sleep(1)

    driver.execute_script("arguments[0].click();", button)

    downloaded_pdf = wait_for_download_pdf(download_dir)

    if dest_path.exists():
        dest_path.unlink()

    shutil.copy2(str(downloaded_pdf), str(dest_path))
    print(f"保存しました: {dest_path}")

    # Acrobatが掴んでいて削除できないことがあるので、削除は試すだけ
    try:
        downloaded_pdf.unlink()
    except PermissionError:
        print(f"元ファイルは使用中のため削除できませんでした: {downloaded_pdf}")


def adobe_download(driver, year, month, base_dir, download_dir):
    ym = f"{year}{month:02d}"

    driver.get(
        "https://account.adobe.com/orders/billing-history?search=AD00404638251CJP"
    )

    input(
        "Adobeの請求履歴画面を表示してください。"
        "最新の請求書・領収書の行が見える状態で Enter: "
    )

    buttons = driver.find_elements(
        By.CSS_SELECTOR,
        '[data-testid="tooltip-button-action"]'
    )

    print("ボタン数:", len(buttons))

    for i, button in enumerate(buttons[:10]):
        print(i, button.get_attribute("aria-label"), button.text)

    invoice_button = buttons[1]
    receipt_button = buttons[4]

    invoice_path = base_dir / f"ADOBE{ym}請求書.pdf"
    receipt_path = base_dir / f"ADOBE{ym}領収書.pdf"

    click_download_button_and_rename(
        driver, invoice_button, download_dir, invoice_path
    )

    buttons = driver.find_elements(
        By.CSS_SELECTOR,
        '[data-testid="tooltip-button-action"]'
    )

    receipt_button = buttons[4]

    click_download_button_and_rename(
        driver, receipt_button, download_dir, receipt_path
    )