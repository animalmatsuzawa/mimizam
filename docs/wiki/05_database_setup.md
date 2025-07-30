# データベース設定ガイド

mimizamは複数のデータベースバックエンドを統一インターフェースでサポートしています。各データベースの技術的特徴を理解して、アプリケーション要件に応じて選択できます。

## 🗄️ サポートされているデータベース

| データベース | 特徴 | 技術的特性 | セットアップ難易度 |
|-------------|------|----------|-------------------|
| **SQLite** | 軽量、ファイルベース | 単一ファイル、組み込み型 | ⭐ 低 |
| **MySQL** | 高性能、スケーラブル | リレーショナル、ACID準拠 | ⭐⭐ 中程度 |
| **PostgreSQL** | 堅牢、機能豊富 | 高度なSQL機能、拡張性 | ⭐⭐ 中程度 |
| **Elasticsearch** | 全文検索、分散処理 | NoSQL、水平スケーリング | ⭐⭐⭐ 複雑 |

## 🚀 統合APIによる使用方法

### Mimizam統合API

すべてのデータベースで同じAPIを使用できます：

```python
from mimizam import (
    create_mimizam_sqlite,
    create_mimizam_mysql,
    create_mimizam_postgresql,
    create_mimizam_elasticsearch
)

# SQLite
with create_mimizam_sqlite("my_music.db") as mimizam:
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist")
    results = mimizam.search_song("query.wav")

# MySQL
with create_mimizam_mysql(
    host="localhost", database="music_db",
    username="user", password="pass"
) as mimizam:
    # 同じAPIでデータベースを透過的に使用

# PostgreSQL
with create_mimizam_postgresql(
    host="localhost", database="music_db", 
    username="user", password="pass"
) as mimizam:
    # 同じAPIでデータベースを透過的に使用

# Elasticsearch
with create_mimizam_elasticsearch(
    host="localhost", index_name="music_index"
) as mimizam:
    # 同じAPIでデータベースを透過的に使用
```

## 📊 SQLite設定

### 基本設定

```python
from mimizam import create_mimizam_sqlite

# ファイルベースデータベース
with create_mimizam_sqlite("fingerprints.db") as mimizam:
    # 使用開始
    pass

# メモリ内データベース（テスト用）
with create_mimizam_sqlite(":memory:") as mimizam:
    # 一時的な使用
    pass
```

### 低レベルAPI

```python
from mimizam import FingerprintDatabase, create_sqlite_config

# カスタム設定
config = create_sqlite_config("custom_path.db")
db = FingerprintDatabase(config)
```

### SQLite設定

```python
# WALモード有効化（パフォーマンス向上）
import sqlite3

conn = sqlite3.connect("fingerprints.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=10000")
conn.execute("PRAGMA temp_store=MEMORY")
conn.close()
```

## 🐬 MySQL設定

### 事前準備

```sql
-- データベース作成
CREATE DATABASE fingerprints_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ユーザー作成（オプション）
CREATE USER 'fingerprint_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON fingerprints_db.* TO 'fingerprint_user'@'localhost';
FLUSH PRIVILEGES;
```

### 基本設定

```python
from mimizam import create_mimizam_mysql

# 基本接続
with create_mimizam_mysql(
    host="localhost",
    database="fingerprints_db",
    username="fingerprint_user",
    password="secure_password",
    port=3306  # オプション
) as mimizam:
    # 使用開始
    pass
```

### 低レベルAPI

```python
from mimizam import FingerprintDatabase, create_mysql_config

# カスタム設定
config = create_mysql_config(
    host="localhost",
    database="fingerprints_db",
    username="fingerprint_user", 
    password="secure_password",
    port=3306
)
db = FingerprintDatabase(config)
```

### MySQL設定

```sql
-- my.cnf設定例
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 128M
max_connections = 200
```

## 🐘 PostgreSQL設定

### 事前準備

```sql
-- データベース作成
CREATE DATABASE fingerprints_db;

-- ユーザー作成（オプション）
CREATE USER fingerprint_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE fingerprints_db TO fingerprint_user;
```

### 基本設定

```python
from mimizam import create_mimizam_postgresql

# 基本接続
with create_mimizam_postgresql(
    host="localhost",
    database="fingerprints_db",
    username="fingerprint_user",
    password="secure_password",
    port=5432  # オプション
) as mimizam:
    # 使用開始
    pass
```

### 低レベルAPI

```python
from mimizam import FingerprintDatabase, create_postgresql_config

# カスタム設定
config = create_postgresql_config(
    host="localhost",
    database="fingerprints_db",
    username="fingerprint_user",
    password="secure_password", 
    port=5432
)
db = FingerprintDatabase(config)
```

### PostgreSQL設定

```sql
-- postgresql.conf設定例
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

## 🔍 Elasticsearch設定

### 基本設定

```python
from mimizam import create_mimizam_elasticsearch

# 基本接続
with create_mimizam_elasticsearch(
    host="localhost",
    port=9200,
    index_name="audio_fingerprints"
) as mimizam:
    # 使用開始
    pass

# 認証付き接続
with create_mimizam_elasticsearch(
    host="localhost",
    port=9200,
    index_name="audio_fingerprints",
    username="elastic",
    password="password"
) as mimizam:
    # 使用開始
    pass
```

### 低レベルAPI

```python
from mimizam import FingerprintDatabase, DatabaseConfig

# カスタム設定
config = DatabaseConfig(
    backend='elasticsearch',
    host="localhost",
    port=9200,
    index_name="audio_fingerprints",
    username="elastic",  # 認証が必要な場合
    password="password"  # 認証が必要な場合
)
db = FingerprintDatabase(config)
```

### シャード・レプリカ設定

```python
# カスタムシャード・レプリカ設定
config = DatabaseConfig(
    backend='elasticsearch',
    host="localhost", 
    port=9200,
    index_name="audio_fingerprints",
    # シャード・レプリカ設定
    es_songs_shards=2,           # 楽曲インデックスのシャード数
    es_songs_replicas=1,         # 楽曲インデックスのレプリカ数
    es_fingerprints_shards=5,    # フィンガープリントインデックスのシャード数
    es_fingerprints_replicas=1   # フィンガープリントインデックスのレプリカ数
)
db = FingerprintDatabase(config)
```

### シャード・レプリカ設定

#### 楽曲インデックス (songs)
- **小規模** (1万曲未満): `es_songs_shards=1, es_songs_replicas=0`
- **中規模** (1-10万曲): `es_songs_shards=2, es_songs_replicas=1`
- **大規模** (10万曲以上): `es_songs_shards=3-5, es_songs_replicas=1-2`

#### フィンガープリントインデックス (fingerprints)
- **小規模** (100万FP未満): `es_fingerprints_shards=2, es_fingerprints_replicas=0`
- **中規模** (100万-1000万FP): `es_fingerprints_shards=3-5, es_fingerprints_replicas=1`
- **大規模** (1000万FP以上): `es_fingerprints_shards=5-10, es_fingerprints_replicas=1-2`

## 📦 パッケージ依存関係

各データベースには対応するPythonパッケージが必要です：

```bash
# MySQL用
pip install mysql-connector-python

# PostgreSQL用  
pip install psycopg2-binary

# Elasticsearch用
pip install elasticsearch

# SQLiteは標準ライブラリに含まれています
```

## 📊 パフォーマンス比較

| データベース | 読み取り性能 | 書き込み性能 | セットアップ | メモリ使用量 | 技術的特性 |
|-------------|-------------|-------------|-------------|-------------|----------|
| SQLite | 中 | 中 | 低 | 低 | 単一プロセス |
| MySQL | 高 | 高 | 中 | 中 | マルチユーザー |
| PostgreSQL | 高 | 高 | 中 | 中 | 高機能SQL |
| Elasticsearch | 最高 | 中 | 複雑 | 高 | 分散アーキテクチャ |

## 🏗️ 技術設定例

### SQLite設定例

```python
# ファイルベースデータベース
with create_mimizam_sqlite("development.db") as mimizam:
    # 楽曲追加
    song_id = mimizam.add_song("test_song.wav", "Test Song", "Test Artist")
    # 検索
    results = mimizam.search_song("query.wav")
```

### MySQL設定例

```python
import os

# MySQL接続設定
with create_mimizam_mysql(
    host="db.example.com",
    port=3306,
    database="fingerprints_db",
    username="app_user",
    password=os.getenv("DB_PASSWORD")  # 環境変数から取得
) as mimizam:
    # 同じAPIでデータベースを使用
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist")
    results = mimizam.search_song("query.wav")
```

### PostgreSQL設定例

```python
# PostgreSQL接続設定
with create_mimizam_postgresql(
    host="postgresql.example.com",
    port=5432,
    database="fingerprints_db", 
    username="app_user",
    password=os.getenv("DB_PASSWORD")
) as mimizam:
    # 同じAPIでデータベースを使用
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist")
    results = mimizam.search_song("query.wav")
```

### Elasticsearch設定例

```python
# Elasticsearch接続設定
with create_mimizam_elasticsearch(
    host="elasticsearch.example.com",
    port=9200,
    index_name="audio_fingerprints",
    # シャード・レプリカ設定
    es_songs_shards=3,
    es_songs_replicas=1,
    es_fingerprints_shards=5,
    es_fingerprints_replicas=1
) as mimizam:
    # 同じAPIでデータベースを使用
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist") 
    results = mimizam.search_song("query.wav")
```

## 🔧 トラブルシューティング

### 接続エラー

1. **データベースサーバーが起動しているか確認**
   ```bash
   # MySQL
   sudo systemctl status mysql
   
   # PostgreSQL
   sudo systemctl status postgresql
   
   # Elasticsearch
   curl -X GET "localhost:9200/"
   ```

2. **認証情報が正しいか確認**
   ```python
   # 接続テスト
   import mysql.connector
   try:
       conn = mysql.connector.connect(
           host="localhost",
           user="fingerprint_user",
           password="secure_password",
           database="fingerprints_db"
       )
       print("✅ 接続成功")
       conn.close()
   except Exception as e:
       print(f"❌ 接続エラー: {e}")
   ```

3. **ファイアウォール設定を確認**
   ```bash
   # ポート確認
   netstat -tlnp | grep :3306  # MySQL
   netstat -tlnp | grep :5432  # PostgreSQL
   netstat -tlnp | grep :9200  # Elasticsearch
   ```

4. **必要なPythonパッケージがインストールされているか確認**
   ```bash
   pip list | grep mysql-connector-python
   pip list | grep psycopg2
   pip list | grep elasticsearch
   ```

### パフォーマンス設定

#### MySQL/PostgreSQL
- インデックスが正しく作成されているか確認
- 接続プールの設定
- クエリキャッシュの有効化

#### Elasticsearch
- 適切なシャード数とレプリカ数を設定
- **小規模構成**: `es_songs_shards=1, es_songs_replicas=0, es_fingerprints_shards=2, es_fingerprints_replicas=0`
- **中規模構成**: `es_songs_shards=2-3, es_songs_replicas=1, es_fingerprints_shards=3-5, es_fingerprints_replicas=1`
- **大規模構成**: `es_songs_shards=3-5, es_songs_replicas=1-2, es_fingerprints_shards=5-10, es_fingerprints_replicas=1-2`

#### SQLite
- WALモードを有効にする（`PRAGMA journal_mode=WAL`）
- キャッシュサイズの調整
- 同期モードの設定


## 🔗 関連ドキュメント

- [基本的な使用方法](./03_basic_usage.md) - 基本操作パターン
- [システムアーキテクチャ](./04_architecture.md) - 全体構成の理解
- [基本的な使用例](./06_basic_examples.md) - 実践的なサンプルコード
- [FAQ](./07_faq.md) - よくある質問とトラブルシューティング
