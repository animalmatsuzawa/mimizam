# データベース移行ツール

mimizamのデータベース移行ツールは、異なるバックエンド間でのデータ移行、スキーマ更新、データベース最適化を自動化します。SQLite、MySQL、PostgreSQL、Elasticsearchの間での移行を安全かつ効率的に実行できます。

## 🔄 移行ツールの概要

### 主要機能

```
データベース移行ツール
├── スキーマ分析
│   ├── テーブル構造確認
│   ├── インデックス分析
│   └── データ整合性チェック
├── データ移行
│   ├── バックエンド間移行
│   ├── バッチ処理
│   └── 進捗監視
├── スキーマ更新
│   ├── 自動スキーマ適用
│   ├── バージョン管理
│   └── ロールバック機能
└── 検証機能
    ├── データ整合性確認
    ├── 移行結果検証
    └── パフォーマンステスト
```

## 🛠️ DatabaseMigrator クラス

### 基本的な使用方法

```python
from mimizam.scripts.migrate_database import DatabaseMigrator
from mimizam import DatabaseConfig

# 移行ツールの初期化
migrator = DatabaseMigrator()

# 移行元設定（SQLite）
source_config = DatabaseConfig(
    backend='sqlite',
    file_path='source_music.db'
)

# 移行先設定（MySQL）
target_config = DatabaseConfig(
    backend='mysql',
    host='localhost',
    database='music_production',
    username='migrator',
    password='secure_password'
)

# データベース移行実行
migrator.migrate(source_config, target_config)
```

### コマンドライン使用

```bash
# スキーマ分析
python scripts/migrate_database.py --analyze --config source_db.json

# データ移行実行
python scripts/migrate_database.py --migrate \
    --source source_db.json \
    --target target_db.json

# 移行検証
python scripts/migrate_database.py --verify \
    --source source_db.json \
    --target target_db.json

# バックアップ作成
python scripts/migrate_database.py --backup --config production_db.json
```

## 📊 スキーマ分析機能

### データベース構造分析

```python
class SchemaAnalyzer:
    """スキーマ分析器"""
    
    def __init__(self, migrator: DatabaseMigrator):
        self.migrator = migrator
    
    def analyze_database_schema(self, config: DatabaseConfig) -> dict:
        """データベーススキーマの詳細分析"""
        
        backend = self.migrator._create_backend(config)
        
        if not backend.connect():
            raise ConnectionError(f"データベース接続失敗: {config.backend}")
        
        try:
            schema_info = {
                'backend_type': config.backend,
                'tables': self._analyze_tables(backend),
                'indexes': self._analyze_indexes(backend),
                'statistics': self._get_database_statistics(backend),
                'schema_version': self._get_schema_version(backend)
            }
            
            return schema_info
            
        finally:
            backend.disconnect()
    
    def _analyze_tables(self, backend) -> dict:
        """テーブル構造分析"""
        
        tables_info = {}
        
        if hasattr(backend, 'connection'):
            cursor = backend.connection.cursor()
            
            # バックエンド別のテーブル情報取得
            if backend.__class__.__name__ == 'SQLiteBackend':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                
                for (table_name,) in cursor.fetchall():
                    tables_info[table_name] = self._analyze_sqlite_table(cursor, table_name)
            
            elif backend.__class__.__name__ == 'MySQLBackend':
                cursor.execute("SHOW TABLES")
                
                for (table_name,) in cursor.fetchall():
                    tables_info[table_name] = self._analyze_mysql_table(cursor, table_name)
        
        return tables_info
    
    def _analyze_sqlite_table(self, cursor, table_name: str) -> dict:
        """SQLiteテーブル分析"""
        
        # テーブル構造取得
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # レコード数取得
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        return {
            'columns': [
                {
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                }
                for col in columns
            ],
            'row_count': row_count
        }

# 使用例
analyzer = SchemaAnalyzer(migrator)

# スキーマ分析実行
schema_info = analyzer.analyze_database_schema(source_config)

print("=== データベーススキーマ分析結果 ===")
print(f"バックエンド: {schema_info['backend_type']}")
print(f"テーブル数: {len(schema_info['tables'])}")

for table_name, table_info in schema_info['tables'].items():
    print(f"\nテーブル: {table_name}")
    print(f"  カラム数: {len(table_info['columns'])}")
    print(f"  レコード数: {table_info['row_count']:,}")
```

## 🔄 データ移行機能

### 高度な移行処理

```python
class AdvancedMigrator(DatabaseMigrator):
    """高度なデータ移行器"""
    
    def __init__(self):
        super().__init__()
        self.migration_log = []
        self.batch_size = 1000
        self.verify_data = True
    
    def migrate_with_progress(self, source_config: DatabaseConfig, 
                            target_config: DatabaseConfig,
                            progress_callback=None) -> dict:
        """進捗監視付きデータ移行"""
        
        import time
        start_time = time.time()
        
        # 移行実行
        migration_results = {
            'start_time': start_time,
            'source_backend': source_config.backend,
            'target_backend': target_config.backend,
            'tables_migrated': 0,
            'records_migrated': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # バックエンド接続
            source_backend = self._create_backend(source_config)
            target_backend = self._create_backend(target_config)
            
            if not source_backend.connect():
                raise ConnectionError("移行元データベース接続失敗")
            
            if not target_backend.connect():
                raise ConnectionError("移行先データベース接続失敗")
            
            # スキーマ作成
            if not target_backend.create_tables():
                raise RuntimeError("移行先テーブル作成失敗")
            
            # データ移行実行
            self._migrate_data_with_batches(
                source_backend, target_backend, 
                migration_results, progress_callback
            )
            
            # 移行検証
            if self.verify_data:
                verification_results = self._verify_migration(
                    source_backend, target_backend
                )
                migration_results['verification'] = verification_results
            
        except Exception as e:
            migration_results['errors'].append(str(e))
            raise
        
        finally:
            # 接続クリーンアップ
            if 'source_backend' in locals():
                source_backend.disconnect()
            if 'target_backend' in locals():
                target_backend.disconnect()
        
        migration_results['end_time'] = time.time()
        migration_results['duration'] = migration_results['end_time'] - start_time
        
        return migration_results
    
    def create_backup(self, config: DatabaseConfig, backup_path: str) -> bool:
        """データベースバックアップ作成"""
        
        try:
            backend = self._create_backend(config)
            
            if not backend.connect():
                raise ConnectionError("バックアップ対象データベース接続失敗")
            
            # バックアップ実行
            if config.backend == 'sqlite':
                return self._backup_sqlite(backend, backup_path)
            elif config.backend == 'mysql':
                return self._backup_mysql(backend, backup_path)
            else:
                print(f"バックアップ未対応: {config.backend}")
                return False
                
        except Exception as e:
            print(f"バックアップエラー: {e}")
            return False
        
        finally:
            if 'backend' in locals():
                backend.disconnect()
    
    def _backup_sqlite(self, backend, backup_path: str) -> bool:
        """SQLiteバックアップ"""
        
        import shutil
        
        try:
            # ファイルコピーによるバックアップ
            source_path = backend.db_path
            shutil.copy2(source_path, backup_path)
            
            print(f"SQLiteバックアップ完了: {backup_path}")
            return True
            
        except Exception as e:
            print(f"SQLiteバックアップエラー: {e}")
            return False

# 使用例
advanced_migrator = AdvancedMigrator()

# 進捗監視付き移行
def progress_callback(progress, message):
    print(f"進捗: {progress*100:.1f}% - {message}")

migration_results = advanced_migrator.migrate_with_progress(
    source_config, target_config, progress_callback
)

print(f"移行結果: {migration_results}")
```

## 🔗 関連ドキュメント

- [データベース設定](./10_database_setup.md) - データベース構成
- [バックエンド比較](./11_backend_comparison.md) - バックエンド選択
- [パフォーマンス最適化](./12_performance_optimization.md) - 移行後最適化
- [テスト](./22_testing.md) - 移行テスト手法
- [品質保証](./24_quality_assurance.md) - 品質管理

## 💡 移行のベストプラクティス

### 1. 事前準備
- 十分なテストとバックアップ
- 移行計画の詳細化
- ダウンタイムの最小化

### 2. 実行時の注意点
- バッチサイズの適切な設定
- 進捗監視とエラーハンドリング
- データ整合性の継続確認

### 3. 移行後の対応
- 性能テストの実施
- アプリケーション動作確認
- 監視体制の構築

mimizamのデータベース移行ツールにより、安全で効率的なデータベース移行が実現できます。
