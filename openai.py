# openai.py
from time import sleep
import shutil
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


def copy_downloaded_pdf(downloaded_pdf, dest_path):
    if dest_path.exists():
        dest_path.unlink()

    shutil.copy2(str(downloaded_pdf), str(dest_path))
    print(f"保存しました: {dest_path}")

    try:
        downloaded_pdf.unlink()
    except PermissionError:
        print(f"元ファイルは使用中のため削除できませんでした: {downloaded_pdf}")


def wait_manual_download_and_copy(download_dir, dest_path, message):
    start_time = time.time()

    input(message)

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
            downloaded_pdf = max(recent_pdfs, key=lambda p: p.stat().st_mtime)
            copy_downloaded_pdf(downloaded_pdf, dest_path)
            return


def openai_download(driver, year, month, base_dir, download_dir):
    ym = f"{year}{month:02d}"

    driver.get("https://chatgpt.com/")

    input(
        "手動でOpenAIの請求履歴から対象月のStripe請求書ページを開いてください。"
        "「請求書をダウンロード」「領収書をダウンロード」が見える状態で Enter: "
    )

    invoice_path = base_dir / f"OPENAI{ym}請求書.pdf"
    receipt_path = base_dir / f"OPENAI{ym}領収書.pdf"

    wait_manual_download_and_copy(
        download_dir,
        invoice_path,
        "これから『請求書をダウンロード』を押してください。押してPDFが落ちたら Enter: "
    )

    wait_manual_download_and_copy(
        download_dir,
        receipt_path,
        "これから『領収書をダウンロード』を押してください。押してPDFが落ちたら Enter: "
    )