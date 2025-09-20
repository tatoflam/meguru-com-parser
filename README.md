# Meguru Construction Works Scraper

このプロジェクトは、めぐる組の[施工実績ページ](https://meguru-construction.com/works/)から各プロジェクトの詳細情報を自動的に収集し、JSON形式で出力するWebスクレイピングツールです。

## 取得する情報

各プロジェクトページから以下の情報を抽出します：

- 所在地
- 竣工年月
- 敷地面積
- 延床面積
- 容積消化
- 構造
- 階数
- 戸数
- コメント

## 必要な環境

- Docker
- Docker Compose

## 使用方法

### 1. プロジェクトのクローン/ダウンロード

```bash
git clone <repository-url>
cd meguru-com-parser
```

### 2. Docker Composeでの実行

```bash
# Docker イメージをビルドして実行
docker-compose up --build

# バックグラウンドで実行する場合
docker-compose up --build -d
```

### 3. 結果の確認

スクレイピングが完了すると、`output/meguru_projects.json` ファイルに結果が保存されます。

#### Docker Composeで実行した場合
```bash
# コンテナの実行状況を確認
docker-compose ps

# 実行完了後、ホスト側のoutputディレクトリに結果が保存される
ls -la output/

# 結果ファイルの確認
cat output/meguru_projects.json

# JSONファイルの行数確認
wc -l output/meguru_projects.json

# 最初の数行を確認
head -20 output/meguru_projects.json

# 最後の数行を確認
tail -20 output/meguru_projects.json
```

#### 直接Pythonで実行した場合
```bash
# 結果ファイルの確認
cat output/meguru_projects.json
```

#### コンテナ内のログを確認する場合
```bash
# リアルタイムでログを確認
docker-compose logs -f meguru-scraper

# 実行完了後のログを確認
docker-compose logs meguru-scraper
```

## 出力形式

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

## ファイル構成

- `scraper.py` - メインのスクレイピングスクリプト
- `requirements.txt` - Python依存関係
- `Dockerfile` - Dockerイメージ設定
- `docker-compose.yml` - Docker Compose設定
- `output/` - 出力ファイル保存ディレクトリ

## 注意事項

- スクレイピング実行時は、サーバーに負荷をかけないよう適切な間隔（1秒）でリクエストを送信します
- ネットワーク接続が必要です
- 対象サイトの構造が変更された場合、スクリプトの修正が必要になる可能性があります

## トラブルシューティング

### Docker関連のエラー

```bash
# Docker イメージとコンテナのクリーンアップ
docker-compose down
docker system prune -f

# 再ビルドして実行
docker-compose up --build
```

### 権限エラー

```bash
# outputディレクトリの権限を確認
chmod 755 output/
