# Docker Compose実行例とファイル確認方法

## Docker Composeでの実行手順

### 1. 実行前の準備
```bash
# 現在のディレクトリ確認
pwd
# /Users/tato/repo/github/tatoflam/meguru-com-parser

# outputディレクトリの存在確認
ls -la output/
```

### 2. Docker Composeで実行
```bash
# フォアグラウンドで実行（ログをリアルタイム表示）
docker-compose up --build

# または、バックグラウンドで実行
docker-compose up --build -d
```

### 3. 実行中の確認
```bash
# コンテナの状態確認
docker-compose ps

# ログの確認（バックグラウンド実行の場合）
docker-compose logs -f meguru-scraper
```

### 4. 実行完了後のファイル確認

#### ボリュームマウントの仕組み
- `docker-compose.yml`の設定: `./output:/app/output`
- ホスト側の`./output`ディレクトリがコンテナ内の`/app/output`にマウント
- コンテナ内で生成されたファイルが自動的にホスト側に保存される

#### ファイル確認コマンド
```bash
# outputディレクトリの内容確認
ls -la output/

# JSONファイルの存在確認
ls -la output/*.json

# ファイルサイズ確認
du -h output/meguru_projects.json

# JSONファイルの内容確認（最初の20行）
head -20 output/meguru_projects.json

# JSONファイルの内容確認（最後の20行）
tail -20 output/meguru_projects.json

# 全体の行数確認
wc -l output/meguru_projects.json

# プロジェクト数の確認（JSONオブジェクトの数）
grep -c '"url":' output/meguru_projects.json
```

### 5. 実行例
```bash
$ docker-compose up --build
Building meguru-scraper
[+] Building 2.3s (10/10) FINISHED
...
meguru-scraper  | Starting to scrape Meguru Construction projects...
meguru-scraper  | Fetching page 1: https://meguru-construction.com/works/
meguru-scraper  | Fetching page 2: https://meguru-construction.com/works/page/2/
meguru-scraper  | Found 28 project pages
meguru-scraper  | Processing 1/28: https://meguru-construction.com/works/lt_nakano/
...
meguru-scraper  | Successfully scraped 28 projects
meguru-scraper  | Data saved to output/meguru_projects.json
meguru-scraper exited with code 0

$ ls -la output/
total 72
drwxr-xr-x   3 user  staff    96 Sep 17 01:13 .
drwxr-xr-x  12 user  staff   384 Sep 17 01:07 ..
-rw-r--r--   1 user  staff 16698 Sep 17 01:13 meguru_projects.json

$ wc -l output/meguru_projects.json
     392 output/meguru_projects.json
```

## 重要なポイント

1. **ボリュームマウント**: `./output:/app/output`により、コンテナ内で生成されたファイルがホスト側に自動保存
2. **ファイルパス**: コンテナ内では`/app/output/meguru_projects.json`、ホスト側では`./output/meguru_projects.json`
3. **権限**: ファイルはコンテナ実行ユーザーの権限で作成されるが、通常は読み取り可能
4. **永続化**: コンテナを削除してもファイルはホスト側に残る
