# データベース設定ガイド

mimizamは複数のデータベースバックエンドを統一インターフェースでサポートしています。

## サポートされているデータベース

- **SQLite**: 軽量、ファイルベース（デフォルト）
- **MySQL**: 高性能、スケーラブル
- **PostgreSQL**: 堅牢、機能豊富  
- **Elasticsearch**: 全文検索、分散処理

## 統合APIによる簡単な使用方法

### Mimizam統合API（推奨）

```python

# SQLite（最も簡単）
with create_mimizam_sqlite("my_music.db") as mimizam:
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist")
    results = mimizam.search_song("query.wav")

# MySQL（拡張性）
with create_mimizam_mysql(
    host="localhost", database="music_db",
    username="user", password="pass"
) as mimizam:
    # 同じAPIでデータベースを透過的に使用

# PostgreSQL（高性能）
with create_mimizam_postgresql(
    host="localhost", database="music_db", 
    username="user", password="pass"
) as mimizam:
    # 同じAPIでデータベースを透過的に使用

# Elasticsearch（分散検索）
with create_mimizam_elasticsearch(
    host="localhost", index_name="music_index"
) as mimizam:
    # 同じAPIでデータベースを透過的に使用
```

## 低レベルAPI

### 統一データベースバックエンド

```python

# SQLite設定
config = create_sqlite_config("custom_path.db")
db = FingerprintDatabase(config)

# MySQL設定
config = create_mysql_config(
    host="localhost",
    database="fingerprints_db",
    username="your_username", 
    password="your_password",
    port=3306
)
db = FingerprintDatabase(config)
```

#### MySQL設定前の準備

```sql
-- データベース作成
CREATE DATABASE fingerprints_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ユーザー作成（オプション）
CREATE USER 'fingerprint_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON fingerprints_db.* TO 'fingerprint_user'@'localhost';
FLUSH PRIVILEGES;
```

### PostgreSQL

```python

config = create_postgresql_config(
    host="localhost",
    database="fingerprints_db",
    username="your_username",
    password="your_password", 
    port=5432  # オプション
)
db = FingerprintDatabase(config)
```

#### PostgreSQL設定前の準備

```sql
-- データベース作成
CREATE DATABASE fingerprints_db;

-- ユーザー作成（オプション）
CREATE USER fingerprint_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE fingerprints_db TO fingerprint_user;
```

### Elasticsearch

```python

# 基本設定
config = DatabaseConfig(
    backend='elasticsearch',
    host="localhost",
    port=9200,
    index_name="audio_fingerprints",
    username="elastic",  # 認証が必要な場合
    password="password"  # 認証が必要な場合
)
db = FingerprintDatabase(config)

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

#### Elasticsearchシャード・レプリカ推奨設定

**楽曲インデックス (songs)**
- 小規模 (1万曲未満): `es_songs_shards=1, es_songs_replicas=0`
- 中規模 (1-10万曲): `es_songs_shards=2, es_songs_replicas=1`
- 大規模 (10万曲以上): `es_songs_shards=3-5, es_songs_replicas=1-2`

**フィンガープリントインデックス (fingerprints)**
- 小規模 (100万FP未満): `es_fingerprints_shards=2, es_fingerprints_replicas=0`
- 中規模 (100万-1000万FP): `es_fingerprints_shards=3-5, es_fingerprints_replicas=1`
- 大規模 (1000万FP以上): `es_fingerprints_shards=5-10, es_fingerprints_replicas=1-2`

**本番環境での推奨事項**
- レプリカ数は少なくとも1以上（可用性のため）
- シャード数はクラスターのノード数を考慮して設定
- パフォーマンスと可用性のバランスを考慮

## パッケージ依存関係

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

## パフォーマンス比較

| データベース  | 読み取り性能 | 書き込み性能 | セットアップ | 推奨用途     |
| ------------- | ------------ | ------------ | ------------ | ------------ |
| SQLite        | 中           | 中           | 簡単         | 開発・小規模 |
| MySQL         | 高           | 高           | 中           | 本番環境     |
| PostgreSQL    | 高           | 高           | 中           | 複雑なクエリ |
| Elasticsearch | 最高         | 中           | 複雑         | 大規模検索   |

## 設定例

### 開発環境
```python
# SQLiteを使用（最も簡単）

with create_mimizam_sqlite("development.db") as mimizam:
    # 楽曲追加
    song_id = mimizam.add_song("test_song.wav", "Test Song", "Test Artist")
    # 検索
    results = mimizam.search_song("query.wav")
```

### 本番環境
```python
# MySQL使用例

with create_mimizam_mysql(
    host="db.example.com",
    port=3306,
    database="fingerprints_production",
    username="app_user",
    password=os.getenv("DB_PASSWORD")
) as mimizam:
    # 同じAPIで本番データベースを使用
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist")
    results = mimizam.search_song("query.wav")
```

### 高性能検索環境
```python
# PostgreSQL使用例（高性能）

with create_mimizam_postgresql(
    host="postgresql.example.com",
    port=5432,
    database="fingerprints_production", 
    username="app_user",
    password=os.getenv("DB_PASSWORD")
) as mimizam:
    # 高性能データベースで同じAPI
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist")
    results = mimizam.search_song("query.wav")

# Elasticsearch使用例（大規模分散検索）

with create_mimizam_elasticsearch(
    host="elasticsearch.example.com",
    port=9200,
    index_name="audio_fingerprints_prod"
) as mimizam:
    # 分散検索で同じAPI
    song_id = mimizam.add_song("song.wav", "Song Title", "Artist") 
    results = mimizam.search_song("query.wav")
```

## トラブルシューティング

### 接続エラー

1. **データベースサーバーが起動しているか確認**
2. **認証情報が正しいか確認**
3. **ファイアウォール設定を確認**
4. **必要なPythonパッケージがインストールされているか確認**

### パフォーマンス最適化

- **MySQL/PostgreSQL**: インデックスが正しく作成されているか確認
- **Elasticsearch**: 適切なシャード数とレプリカ数を設定
  - 開発環境: `es_songs_shards=1, es_songs_replicas=0, es_fingerprints_shards=2, es_fingerprints_replicas=0`
  - 本番環境: `es_songs_shards=2-3, es_songs_replicas=1, es_fingerprints_shards=3-5, es_fingerprints_replicas=1`
  - 大規模環境: `es_songs_shards=3-5, es_songs_replicas=1-2, es_fingerprints_shards=5-10, es_fingerprints_replicas=1-2`
- **SQLite**: WALモードを有効にする（pragma journal_mode=WAL）

## セキュリティ考慮事項

1. **データベース認証情報を環境変数で管理**
2. **SSL/TLS接続を使用（本番環境）**
3. **最小権限の原則でユーザー権限を設定**
4. **定期的なバックアップの実施**
