"""
Web自動操作・自動化スクリプト
Playwrightを使用してWebブラウザの操作を自動化します。
"""

import asyncio
import os
from playwright.async_api import async_playwright, Page
from dotenv import load_dotenv

# ==============================
# 設定
# ==============================
load_dotenv()
TARGET_URL = os.getenv("TARGET_URL", "https://your-target-url.com/list")
WAIT_MS = 1000
HEADLESS = False


async def process_one_page(page: Page, page_num: int) -> dict:
    print(f"\n{'='*50}")
    print(f"  ページ {page_num} 処理開始")
    print(f"{'='*50}")

    results = {"total": 0, "already_linked": 0, "newly_linked": 0, "no_button": 0}
    list_url = page.url

    # 対象リンクを全件取得
    links = page.locator("a[href*='/target_path/']")
    total = await links.count()

    if total == 0:
        print("対象ボタンが見つかりません。")
        return results

    # href・IDを全件取得してからループ
    items = []
    for i in range(total):
        href = await links.nth(i).get_attribute("href")
        if href:
            full_url = f"{TARGET_URL.split('/')[0]}//{TARGET_URL.split('/')[2]}{href}" if href.startswith("/") else href
            try:
                row = links.nth(i).locator("xpath=ancestor::div[contains(@class,'ift-row')]")
                system_id = (await row.locator(".ift-cell").nth(1).inner_text()).strip()
            except Exception:
                system_id = "不明"
            items.append((full_url, system_id))

    print(f"対象リンク: {len(items)}件 取得完了")
    results["total"] = len(items)

    for i, (url, system_id) in enumerate(items):
        print(f"\n--- [{i+1}/{len(items)}] SystemID: {system_id} ---")

        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(WAIT_MS)

        linked = await check_and_execute(page)

        if linked == "already":
            results["already_linked"] += 1
        elif linked == "newly":
            results["newly_linked"] += 1
        else:
            results["no_button"] += 1

        await page.goto(list_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(WAIT_MS)
        print(f"  → 一覧に戻りました")

    return results


async def check_and_execute(page: Page) -> str:
    """処理済み確認・未処理なら自動実行"""
    if await page.locator("text=処理済み").count() > 0:
        print(f"  ✅ 処理済み確認 → スキップ")
        return "already"

    print(f"  ⚠️  未処理 → 実行ボタンを探します")

    btn = page.locator("button.btn-info:has-text('実行')")
    if await btn.count() == 0:
        print(f"  ❌ 実行ボタンが見つかりません → スキップ")
        return "no_button"

    await page.evaluate("""
        const form = document.querySelector('form[data-turbo-confirm]');
        if (form) {
            form.removeAttribute('data-turbo-confirm');
            form.submit();
        }
    """)
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    await page.wait_for_timeout(1000)

    print(f"  🔗 実行完了")
    return "newly"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"対象URLを開きます: {TARGET_URL}")
        await page.goto(TARGET_URL)

        print("\n>>> ログインして対象ページを開いたらEnterを押してください <<<")
        input()

        total_summary = {"pages": 0, "total": 0, "already_linked": 0, "newly_linked": 0, "no_button": 0}
        page_num = 1

        while True:
            result = await process_one_page(page, page_num)
            total_summary["pages"] += 1
            total_summary["total"] += result["total"]
            total_summary["already_linked"] += result["already_linked"]
            total_summary["newly_linked"] += result["newly_linked"]
            total_summary["no_button"] += result["no_button"]

            print(f"\n{'='*50}")
            print(f"  ページ {page_num} 完了！")
            print(f"  処理件数     : {result['total']}件")
            print(f"  処理済み     : {result['already_linked']}件")
            print(f"  新たに実行   : {result['newly_linked']}件")
            print(f"  ボタンなし   : {result['no_button']}件")
            print(f"{'='*50}")
            print()
            print("  次のページがあれば手動で移動してからEnterを押してください。")
            print("  全ページ完了なら 'q' + Enter で終了します。")

            user_input = input(">>> ").strip().lower()
            if user_input == "q":
                break
            page_num += 1

        print(f"\n{'='*50}")
        print(f"  全処理完了！")
        print(f"  処理ページ数   : {total_summary['pages']}ページ")
        print(f"  処理総件数     : {total_summary['total']}件")
        print(f"  処理済み       : {total_summary['already_linked']}件")
        print(f"  新たに実行     : {total_summary['newly_linked']}件")
        print(f"  ボタンなし     : {total_summary['no_button']}件")
        print(f"{'='*50}")

        print("\nブラウザを閉じるにはEnterを押してください...")
        input()
        await browser.close()


if __name__ == "__main__":
    if __import__("sys").platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
```

あと`.gitignore`ファイルも作って下記を貼り付けてください！
```
.env
__pycache__/
*.pyc
