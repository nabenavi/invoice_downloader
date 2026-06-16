from pathlib import Path
from time import sleep
from datetime import datetime
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


YEAR = 2026
MONTH = 6
YM = f"{YEAR}{MONTH:02d}"

BASE_DIR = Path.home() / "Documents" / "請求書領収書" / YM
DOWNLOAD_DIR = BASE_DIR / "_download"

BASE_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def make_driver():
    options = Options()

    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def wait_enter(message):
    input(f"\n{message}\n完了したら Enter を押してください: ")


def wait_for_pdf():
    print("PDFのダウンロードを待っています...")
    before = set(DOWNLOAD_DIR.glob("*.pdf"))

    while True:
        sleep(1)

        # Chromeの未完了ダウンロード
        if list(DOWNLOAD_DIR.glob("*.crdownload")):
            continue

        after = set(DOWNLOAD_DIR.glob("*.pdf"))
        new_files = list(after - before)

        if new_files:
            latest = max(new_files, key=lambda p: p.stat().st_mtime)
            print(f"検出: {latest.name}")
            return latest


def save_latest_pdf_as(filename):
    pdf = wait_for_pdf()
    dest = BASE_DIR / filename

    if dest.exists():
        dest.unlink()

    shutil.move(str(pdf), str(dest))
    print(f"保存しました: {dest}")


def main():
    driver = make_driver()

    # 1 三井住友
    smbc_url = f"https://www.smbc-card.com/memx/web_meisai/top/index.html?p01={YM}"
    driver.get(smbc_url)
    wait_enter("三井住友カードのPDFをダウンロードしてください")
    save_latest_pdf_as(f"法人カード明細{YM}.pdf")

    # 2 日経
    nikkei_url = "https://id.nikkei.com/account/payments/histories"
    driver.get(nikkei_url)
    wait_enter("日経の明細ボタンを押して、PDFをダウンロードしてください")
    save_latest_pdf_as(f"nikkei{YM}.pdf")

    # 3 Adobe
    adobe_url = "https://account.adobe.com/orders/billing-history?search=AD00404638251CJP"
    driver.get(adobe_url)

    wait_enter("Adobeの請求書PDFをダウンロードしてください")
    save_latest_pdf_as(f"ADOBE{YM}請求書.pdf")

    wait_enter("Adobeの領収書PDFをダウンロードしてください")
    save_latest_pdf_as(f"ADOBE{YM}領収書.pdf")

    # 4 OpenAI
    openai_url = "https://chatgpt.com/#settings/Billing"
    driver.get(openai_url)

    wait_enter("OpenAIの請求書PDFをダウンロードしてください")
    save_latest_pdf_as(f"OPENAI{YM}請求書.pdf")

    wait_enter("OpenAIの領収書PDFをダウンロードしてください")
    save_latest_pdf_as(f"OPENAI{YM}領収書.pdf")

    print("\nすべて完了しました。")
    print(BASE_DIR)

    wait_enter("ブラウザを閉じます")
    driver.quit()


if __name__ == "__main__":
    main()