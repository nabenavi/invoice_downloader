# openai.py

from time import sleep
from smbc import save_current_page_as_pdf
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_download_pdf(download_dir):
    before = set(download_dir.glob("*.pdf"))

    while True:
        sleep(1)

        if list(download_dir.glob("*.crdownload")):
            continue

        after = set(download_dir.glob("*.pdf"))
        new_files = list(after - before)

        if new_files:
            return max(new_files, key=lambda p: p.stat().st_mtime)


def download_and_rename(driver, download_dir, dest_path, button_xpath):
    before_handles = set(driver.window_handles)

    button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, button_xpath))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        button
    )

    sleep(1)

    driver.execute_script("arguments[0].click();", button)

    downloaded_pdf = wait_for_download_pdf(download_dir)

    if dest_path.exists():
        dest_path.unlink()

    shutil.move(str(downloaded_pdf), str(dest_path))
    print(f"保存しました: {dest_path}")


def openai_download(driver, year, month, base_dir):
    ym = f"{year}{month:02d}"

    driver.get("https://chatgpt.com/")

    input(
        "手動でOpenAIの請求履歴を開き、"
        "対象月のStripe請求書ページを表示してください。"
        "請求書ページが表示されたら Enter: "
    )

    # 請求書を保存：これは前回成功した方式
    invoice_pdf_path = base_dir / f"OPENAI{ym}請求書.pdf"
    save_current_page_as_pdf(driver, invoice_pdf_path)

    input(
        "同じStripeページで、手動で「領収書をダウンロード」または"
        "領収書表示ページを開いてください。"
        "領収書画面が表示されたら Enter: "
    )

    # 領収書を保存
    receipt_pdf_path = base_dir / f"OPENAI{ym}領収書.pdf"
    save_current_page_as_pdf(driver, receipt_pdf_path)