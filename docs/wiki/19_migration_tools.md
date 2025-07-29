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

# データベーススキーマ移行実行
import subprocess

# スキーマ分析
result = subprocess.run(['python', 'scripts/migrate_database.py', '--analyze'], 
                       capture_output=True, text=True)
print("分析結果:", result.stdout)

# スキーマ移行実行
result = subprocess.run(['python', 'scripts/migrate_database.py', '--migrate'], 
                       capture_output=True, text=True)
print("移行結果:", result.stdout)
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
def analyze_database_schema(db_path: str) -> dict:
    """データベーススキーマ分析"""
    from scripts.migrate_database import DatabaseMigrator
    
    migrator = DatabaseMigrator()
    
    # SQLiteスキーマチェック
    schema_info = migrator.check_sqlite_schema(db_path)
    
    return {
        'database_path': db_path,
        'schema_status': schema_info,
        'analysis_method': 'command_line_tool'
    }

def get_database_statistics(db_path: str) -> dict:
    """データベース統計情報取得"""
    import sqlite3
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル一覧取得
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = cursor.fetchall()
        
        stats = {'tables': {}}
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            stats['tables'][table_name] = {'row_count': row_count}
        
        conn.close()
        return stats
        
    except Exception as e:
        return {'error': str(e)}

# 使用例
schema_info = analyze_database_schema('music.db')
stats = get_database_statistics('music.db')

print("=== データベーススキーマ分析結果 ===")
print(f"データベース: {schema_info['database_path']}")
print(f"スキーマ状態: {schema_info['schema_status']}")

if 'tables' in stats:
    print(f"テーブル数: {len(stats['tables'])}")
    for table_name, table_info in stats['tables'].items():
        print(f"  {table_name}: {table_info['row_count']:,}件")
```

## 🔄 データ移行機能

### 高度な移行処理

```python
def migrate_with_progress(source_db_path: str, progress_callback=None) -> dict:
    """進捗監視付きデータ移行"""
    import time
    import subprocess
    from scripts.migrate_database import DatabaseMigrator
    
    start_time = time.time()
    migration_results = {
        'start_time': start_time,
        'source_database': source_db_path,
        'errors': [],
        'warnings': []
    }
    
    try:
        migrator = DatabaseMigrator()
        
        # スキーマチェック
        if progress_callback:
            progress_callback(0.2, "スキーマ分析中...")
        
        schema_status = migrator.check_sqlite_schema(source_db_path)
        migration_results['schema_check'] = schema_status
        
        # 移行実行
        if progress_callback:
            progress_callback(0.5, "スキーマ移行実行中...")
        
        migration_status = migrator._migrate_sqlite({'file_path': source_db_path})
        migration_results['migration_status'] = migration_status
        
        if progress_callback:
            progress_callback(1.0, "移行完了")
            
    except Exception as e:
        migration_results['errors'].append(str(e))
        raise
    
    migration_results['end_time'] = time.time()
    migration_results['duration'] = migration_results['end_time'] - start_time
    
    return migration_results

def create_database_backup(db_path: str, backup_path: str) -> bool:
    """データベースバックアップ作成"""
    import shutil
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"バックアップ完了: {backup_path}")
        return True
    except Exception as e:
        print(f"バックアップエラー: {e}")
        return False

# 使用例
def progress_callback(progress, message):
    print(f"進捗: {progress*100:.1f}% - {message}")

# バックアップ作成
backup_success = create_database_backup('music.db', 'music_backup.db')

# 進捗監視付き移行
if backup_success:
    migration_results = migrate_with_progress('music.db', progress_callback)
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
