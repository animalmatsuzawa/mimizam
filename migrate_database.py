#!/usr/bin/env python3
"""
データベーススキーマ移行ユーティリティ
matsu582のGitHubコメント対応: "meta"カラムデータベーススキーマエラーの解決
"""

import sqlite3
import os
import sys
import json
from typing import List, Dict, Any

def check_database_schema(db_path: str) -> Dict[str, Any]:
    """データベーススキーマを確認"""
    if not os.path.exists(db_path):
        return {"exists": False, "error": f"Database file not found: {db_path}"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(songs)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        has_meta_column = "meta" in column_names
        
        cursor.execute("SELECT COUNT(*) FROM songs")
        song_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
        fingerprint_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "exists": True,
            "has_meta_column": has_meta_column,
            "columns": column_names,
            "song_count": song_count,
            "fingerprint_count": fingerprint_count,
            "schema_version": "new" if has_meta_column else "old"
        }
        
    except Exception as e:
        return {"exists": True, "error": f"Database access error: {e}"}

def migrate_database_schema(db_path: str, backup: bool = True) -> Dict[str, Any]:
    """データベーススキーマを移行してmetaカラムを追加"""
    
    if backup:
        backup_path = f"{db_path}.backup"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"バックアップ作成: {backup_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("ALTER TABLE songs ADD COLUMN meta TEXT")
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Schema migration completed successfully"}
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            return {"success": True, "message": "Meta column already exists"}
        else:
            return {"success": False, "error": f"Migration failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}

def analyze_databases() -> None:
    """既存のデータベースファイルを分析"""
    print("=== データベーススキーマ分析レポート ===")
    print("matsu582のGitHubコメント対応: 'meta'カラムデータベーススキーマエラーの調査\n")
    
    db_files = []
    for file in os.listdir("."):
        if file.endswith(".db"):
            db_files.append(file)
    
    if not db_files:
        print("データベースファイルが見つかりません。")
        return
    
    print(f"発見されたデータベースファイル: {len(db_files)}個")
    
    migration_needed = []
    
    for db_file in db_files:
        print(f"\n--- {db_file} ---")
        schema_info = check_database_schema(db_file)
        
        if "error" in schema_info:
            print(f"❌ エラー: {schema_info['error']}")
            continue
        
        print(f"スキーマバージョン: {schema_info['schema_version']}")
        print(f"metaカラム存在: {'✅ あり' if schema_info['has_meta_column'] else '❌ なし'}")
        print(f"楽曲数: {schema_info['song_count']}")
        print(f"フィンガープリント数: {schema_info['fingerprint_count']}")
        print(f"カラム一覧: {', '.join(schema_info['columns'])}")
        
        if not schema_info['has_meta_column']:
            migration_needed.append(db_file)
    
    if migration_needed:
        print(f"\n=== 移行が必要なデータベース: {len(migration_needed)}個 ===")
        for db_file in migration_needed:
            print(f"- {db_file}")
        
        print("\n=== 問題の詳細 ===")
        print("1. 既存のデータベースファイルには'meta'カラムが存在しない")
        print("2. 新しいスキーマ定義では'meta TEXT'カラムが含まれている")
        print("3. examples/mimizam_demo.pyでSongオブジェクトにmetaフィールドを使用している")
        print("4. データベースとコードのスキーマ不整合によりエラーが発生")
        
        print("\n=== 解決方法 ===")
        print("A. 自動移行: migrate_database.py --migrate を実行")
        print("B. 手動移行: ALTER TABLE songs ADD COLUMN meta TEXT; を実行")
        print("C. データベース再作成: 既存のデータベースファイルを削除して新規作成")
        
    else:
        print("\n✅ 全てのデータベースが最新のスキーマを使用しています。")

def migrate_all_databases() -> None:
    """全ての古いデータベースを移行"""
    print("=== データベーススキーマ移行実行 ===\n")
    
    db_files = [f for f in os.listdir(".") if f.endswith(".db")]
    
    if not db_files:
        print("データベースファイルが見つかりません。")
        return
    
    migrated_count = 0
    
    for db_file in db_files:
        schema_info = check_database_schema(db_file)
        
        if "error" in schema_info:
            print(f"❌ {db_file}: スキップ - {schema_info['error']}")
            continue
        
        if schema_info['has_meta_column']:
            print(f"✅ {db_file}: 既に最新スキーマ")
            continue
        
        print(f"🔄 {db_file}: 移行中...")
        result = migrate_database_schema(db_file)
        
        if result['success']:
            print(f"✅ {db_file}: 移行完了 - {result['message']}")
            migrated_count += 1
        else:
            print(f"❌ {db_file}: 移行失敗 - {result['error']}")
    
    print(f"\n移行完了: {migrated_count}個のデータベース")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--migrate":
            migrate_all_databases()
        elif sys.argv[1] == "--analyze":
            analyze_databases()
        else:
            print("使用方法:")
            print("  python migrate_database.py --analyze   # データベース分析")
            print("  python migrate_database.py --migrate   # スキーマ移行実行")
    else:
        analyze_databases()

if __name__ == "__main__":
    main()
