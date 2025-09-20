# Meguru Construction Website Scraper

このプロジェクトは、めぐる組のWebサイトから各種情報を自動的に収集し、JSON形式で出力するWebスクレイピングツールです。

## 機能

### 1. 施工実績スクレイピング (Works)
- URL: https://meguru-construction.com/works/
- 取得情報: 所在地、竣工年月、敷地面積、延床面積、容積消化、構造、階数、戸数、コメント

### 2. FAQ スクレイピング (FAQ)
- URL: https://meguru-construction.com/faq/
- 取得情報: カテゴリ、質問、回答
- カテゴリ: 企画、調達、設計、施工、運用

## 必要な環境

- Python 3.11+
- Docker & Docker Compose (オプション)

## インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd meguru-com-parser

# 依存関係のインストール
pip install -r requirements.txt
```

## 使用方法

### コマンドライン実行

```bash
# 施工実績のスクレイピング (4ページ)
python main.py works

# 施工実績のスクレイピング (2ページのみ)
python main.py works --pages 2

# FAQのスクレイピング
python main.py faq

# 全てのスクレイピング (施工実績 + FAQ)
python main.py all

# カスタム出力ファイル名
python main.py works --output my_projects.json

# ヘルプの表示
python main.py --help
```

### Docker Compose実行

```bash
# 全てのスクレイピング (デフォルト)
docker-compose up --build

# 施工実績のみ
docker-compose run --rm meguru-scraper python main.py works

# FAQのみ
docker-compose run --rm meguru-scraper python main.py faq
```

## 出力ファイル

### 施工実績 (meguru_projects.json)
```json
[
  {
    "url": "https://meguru-construction.com/works/granqual_my/",
    "project_name": "Granqual Koishikawa グランクオール小石川",
    "location": "東京都文京区",
    "completion_date": "2025年7月",
    "site_area": "137.45㎡",
    "floor_area": "480.90㎡",
    "volume_consumption": "最大360%中328%",
    "structure": "壁式RC共同住宅",
    "floors": "地下1階＋地上4階建て",
    "units": "10戸（全戸2LDK）",
    "comment": "谷地での地下水漏出を完全にコントロールしながら仕上げた、全戸2LDK以上で分譲住宅仕様の案件。"
  }
]
```

### FAQ (meguru_faq.json)
```json
[
  {
    "category": "企画",
    "question_number": 1,
    "question": "土地や企画は自分で持ち込む必要がありますか？",
    "answer": "持ち込んでいただく必要はありません。弊社で土地を探して企画化を致します。ただし、持ち込みの土地や企画にも当然対応できます。"
  }
]
```

## プロジェクト構造

```
meguru-com-parser/
├── main.py                 # メインCLIインターフェース
├── scrapers/               # スクレイパーモジュール
│   ├── __init__.py
│   ├── base.py            # ベーススクレイパークラス
│   ├── works_scraper.py   # 施工実績スクレイパー
│   └── faq_scraper.py     # FAQスクレイパー
├── output/                # 出力ファイル保存ディレクトリ
├── requirements.txt       # Python依存関係
├── Dockerfile            # Dockerイメージ設定
├── docker-compose.yml    # Docker Compose設定
└── README.md             # このファイル
```

## 機能拡張

新しいスクレイピング対象を追加する場合：

1. `scrapers/` ディレクトリに新しいスクレイパーファイルを作成
2. `BaseScraper` クラスを継承
3. `scrape()` と `validate_data()` メソッドを実装
4. `main.py` にスクレイパーを追加

例:
```python
from scrapers.base import BaseScraper

class NewScraper(BaseScraper):
    def scrape(self):
        # スクレイピングロジック
        pass
    
    def validate_data(self, data):
        # データ検証ロジック
        pass
```

## 実行例

```bash
$ python main.py all

Scraping all content (works + FAQ)...
Scraping construction works (max 4 pages)...
2025-09-17 06:49:13,117 - WorksScraper - INFO - Starting WorksScraper...
...
Scraping FAQ...
2025-09-17 06:49:07,600 - FAQScraper - INFO - Starting FAQScraper...
...

==================================================
SCRAPING SUMMARY
==================================================
WORKS:
  Items scraped: 28
  Output file: output/meguru_projects.json
FAQ:
  Items scraped: 50
  Output file: output/meguru_faq.json

Total items scraped: 78

Scraping completed successfully!
```

## 注意事項

- スクレイピング実行時は、サーバーに負荷をかけないよう適切な間隔（1秒）でリクエストを送信
- ネットワーク接続が必要
- 対象サイトの構造が変更された場合、スクレイパーの修正が必要になる可能性あり
- 施工実績は最大4ページに制限（設定変更可能）

## トラブルシューティング

### Docker関連のエラー
```bash
docker-compose down
docker system prune -f
docker-compose up --build
```

### 権限エラー
```bash
chmod 755 output/
```

### モジュールインポートエラー
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python main.py works
