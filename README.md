# Web自動化ツール（Playwright）

Playwrightを使用してWebブラウザの操作を自動化するツールです。

## 機能
- Webページの自動操作・クリック
- ページネーション対応の一括処理
- 処理結果のログ出力
- 処理済み・未処理の自動判定とスキップ

## 使用技術
- Python 3.x
- Playwright
- asyncio

## 使い方
1. リポジトリをクローン
2. 必要なライブラリをインストール
```bash
pip install playwright
playwright install chromium
```
3. `.env`ファイルを作成してURLを設定
```
TARGET_URL=https://your-target-url.com
```
4. スクリプトを実行
```bash
python main.py
```

## 処理フロー
1. ブラウザが起動
2. 手動でログイン
3. Enterを押すと自動処理開始
4. ページごとに処理結果を表示
5. 次ページは手動で移動してEnter
6. 全完了後に`q`で終了

## 出力例
```
処理件数     : 10件
連携成功済み : 8件
新たに連携   : 2件
ボタンなし   : 0件
```
